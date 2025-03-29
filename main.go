package main

import (
	"encoding/json"
	"energy-scheduler/plugins" // Correct import path
	"net/http"

	"k8s.io/klog/v2"
	app "k8s.io/kubernetes/cmd/kube-scheduler/app"
)

func main() {
	klog.Info("Starting Energy Efficient Scheduler Plugin...")
	defer klog.Flush()
	nodeName := "node1"
	score, err := callKubeRLBridge(nodeName)
	klog.Info("Print score:", score, err)

	command := app.NewSchedulerCommand(
		app.WithPlugin(plugins.PluginName, plugins.New), // Register plugin
	)

	if err := command.Execute(); err != nil {
		klog.Fatal(err)
	}

	select {} // Keep running
}

func callKubeRLBridge(node string) (int64, error) {
	resp, err := http.Get("http://kuberlbridge.kube-system.svc.cluster.local:8080/score")
	klog.Info("resp...", resp)

	if err != nil {
		return 0, err
	}
	defer resp.Body.Close()

	var result struct {
		Score int64 `json:"score"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return 0, err
	}

	return result.Score, nil

}
