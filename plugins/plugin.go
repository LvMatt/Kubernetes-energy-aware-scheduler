package plugins

import (
	"context"
	"encoding/json"
	"fmt"
	"math"
	"net/http"
	"strings"

	v1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/klog/v2"
	"k8s.io/kubernetes/pkg/scheduler/framework"
)

const PluginName = "EnergyEfficientScheduler"

type EnergyEfficientPlugin struct {
	handle framework.Handle
}

type BestNodeState struct {
	NodeName string
}

var _ framework.StateData = &BestNodeState{}

func (b *BestNodeState) Clone() framework.StateData {
	return &BestNodeState{
		NodeName: b.NodeName,
	}
}

var _ framework.FilterPlugin = &EnergyEfficientPlugin{}
var _ framework.PreScorePlugin = &EnergyEfficientPlugin{}
var _ framework.ScorePlugin = &EnergyEfficientPlugin{}
var _ framework.PreFilterPlugin = &EnergyEfficientPlugin{}

func New(ctx context.Context, obj runtime.Object, handle framework.Handle) (framework.Plugin, error) {
	klog.Info("Initializing Energy Efficient Plugin...")
	plugin := &EnergyEfficientPlugin{handle: handle}
	return plugin, nil
}

func (p *EnergyEfficientPlugin) Name() string {
	return PluginName
}

func (p *EnergyEfficientPlugin) Filter(ctx context.Context, state *framework.CycleState, pod *v1.Pod, nodeInfo *framework.NodeInfo) *framework.Status {
	podPriority := 0
	appType := pod.Labels["app"] // Expecting "app" or "job"

	if pod.Spec.Priority != nil {
		podPriority = int(*pod.Spec.Priority)
	}
	klog.Info("Filter: podPriority", podPriority)
	klog.Info("Filter: appType", appType)

	var nodeCpuTotal int64 = nodeInfo.Allocatable.MilliCPU
	var nodeMemoryTotal int64 = nodeInfo.Allocatable.Memory

	var nodeCpuInUse int64 = nodeInfo.Requested.MilliCPU
	var nodeMemoryInUse int64 = nodeInfo.Requested.Memory

	var nodeCpuInUsePercentage = (float64(nodeCpuInUse) / float64(nodeCpuTotal)) * 100
	nodeCpuInUsePercentageRounded := math.Round(nodeCpuInUsePercentage*100) / 100

	nodeMemoryInUsePercentage := (float64(nodeMemoryInUse) / float64(nodeMemoryTotal)) * 100
	nodeMemoryInUsePercentageRounded := math.Round(nodeMemoryInUsePercentage*100) / 100

	if appType == "app" {
		if nodeCpuInUsePercentageRounded > 99 || nodeMemoryInUsePercentageRounded > 99 {
			return framework.NewStatus(framework.Error, "CPU or memory usage too high for 'app' pod")
		}
	} else if appType == "job" {
		if nodeCpuInUsePercentageRounded > 95 || nodeMemoryInUsePercentageRounded > 95 {
			return framework.NewStatus(framework.Error, "CPU or memory usage too high for 'job' pod")
		}
	} else {
		return framework.NewStatus(framework.Error, "Unknown app label: must be 'app' or 'job'")
	}

	if nodeInfo.Node() == nil {
		return framework.NewStatus(framework.Error, "Node not found")
	}
	return framework.NewStatus(framework.Success)
}

func (p *EnergyEfficientPlugin) PreScore(ctx context.Context, state *framework.CycleState, pod *v1.Pod, nodes []*framework.NodeInfo) *framework.Status {
	klog.Info("PreScore: Sending all nodes to RL model")

	var nodeNames []string
	for _, nodeInfo := range nodes {
		nodeNames = append(nodeNames, nodeInfo.Node().Name)
	}
	klog.Info("PreScore: nodeNames", nodeNames)

	var podName string = pod.Name
	var podPriority *int32 = pod.Spec.Priority
	var podSchedulerNameAffiliation string = pod.Spec.SchedulerName

	// bestNode, err := callKubeRLBridgeForBestNode(pod, nodeNames)
	bestNode, errMsg, statusCode := callKubeRLBridgeForBestNode(podName, nodeNames, podPriority, podSchedulerNameAffiliation)
	klog.Info("errMsg, statusCode", errMsg, statusCode)
	klog.Info("bestNode__", bestNode)

	if statusCode != 200 {
		klog.Error("RL model returned error:", errMsg, "with statusCode:", statusCode)
		return framework.NewStatus(framework.Error, fmt.Sprintf("Error in RL model: %d", statusCode))
	}

	klog.Infof("RL model selected best node: %s", bestNode)

	if bestNode == "" {
		klog.Error("Received empty bestNode from RL model")
		return framework.NewStatus(framework.Error, "Received empty bestNode")
	}

	state.Write("bestNode", &BestNodeState{NodeName: bestNode})

	return framework.NewStatus(framework.Success)
}

func (p *EnergyEfficientPlugin) Score(ctx context.Context, state *framework.CycleState, pod *v1.Pod, nodeName string) (int64, *framework.Status) {
	val, err := state.Read("bestNode")
	if err != nil {
		klog.Error("Failed to read bestNode from CycleState: ", err)
		return 0, framework.NewStatus(framework.Error, "bestNode not found in CycleState")
	}

	// Ensure proper type assertion
	bestNodeState, ok := val.(*BestNodeState)
	if !ok {
		klog.Error("Invalid bestNode type in CycleState")
		return 0, framework.NewStatus(framework.Error, "Invalid bestNode type")
	}

	klog.Infof("Best node from state: %s", bestNodeState.NodeName)
	klog.Infof("Scoring node: %s", nodeName)

	if nodeName != bestNodeState.NodeName {
		klog.Info("Node is not the best node, assigning low score")
		return 0, framework.NewStatus(framework.Success)
	}

	klog.Info("Assigning high score to the best node")
	return 100, framework.NewStatus(framework.Success)

}

//func callKubeRLBridge(nodeName string, podName string, podPriority *int32, podSchedulerNameAffilation string) (int64, string, error) {
// local purpose only: http://0.0.0.0:3000/score
/* url := fmt.Sprintf("http://kuberlbridge.kube-system.svc.cluster.local:3000/score?nodeName=%s&podName=%s&podPriority=%d&podSchedulerNameAffilation=%s",
nodeName, podName, podPriority, podSchedulerNameAffilation) */
func callKubeRLBridgeForBestNode(podName string, nodes []string, podPriority *int32, podSchedulerNameAffiliation string) (string, string, int) {
	joinedNodes := strings.Join(nodes, ",")
	klog.Infof("nodes: %v, podName: %s, podPriority: %d, podSchedulerNameAffiliation: %s", nodes, podName, *podPriority, podSchedulerNameAffiliation)

	url := fmt.Sprintf("http://kuberlbridge.kube-system.svc.cluster.local:3000/score?nodes=%s&podName=%s&podPriority=%d&podSchedulerNameAffilation=%s",
		joinedNodes, podName, *podPriority, podSchedulerNameAffiliation)

	klog.Infof("Sending request to: %s", url)
	resp, err := http.Get(url)
	if err != nil {
		klog.Errorf("Error calling URL: %v", err)
		return "", "Error", 400
	}
	defer resp.Body.Close()

	// Decode JSON response
	var result struct {
		Node       string `json:"bestNode"`
		Error      string `json:"errorMsg"`
		StatusCode int    `json:"statusCode"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		klog.Errorf("Error decoding response: %v", err)
		return "", "Error", 400
	}

	klog.Infof("Response received: %+v", result)
	return result.Node, result.Error, result.StatusCode
}

func (p *EnergyEfficientPlugin) ScoreExtensions() framework.ScoreExtensions {
	return nil
}

func (p *EnergyEfficientPlugin) PreFilter(ctx context.Context, state *framework.CycleState, pod *v1.Pod) (*framework.PreFilterResult, *framework.Status) {
	klog.Infof("PreFilter called for pod %s", pod.Name)
	return nil, framework.NewStatus(framework.Success)
}

func (p *EnergyEfficientPlugin) PreFilterExtensions() framework.PreFilterExtensions {
	return nil
}
