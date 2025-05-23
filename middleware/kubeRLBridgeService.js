const axios = require("axios");
//const OBSERVABILITY_SERVICE_URL = 'http://127.0.0.1:5001'
const OBSERVABILITY_SERVICE_URL = 'http://observability-service.kube-system.svc.cluster.local:5001';
const RL_MODEL_URL = "http://rl-scheduler.kube-system.svc.cluster.local:8000/schedule";

async function getMemoryMetricsFromObservabilityService(nodes) {
	try {
		const url = `${OBSERVABILITY_SERVICE_URL}/metrics/node-memory?nodes=${nodes}`;
		const metricsMemoryReq = await axios.get(url);
		const metricsMemoryData = await metricsMemoryReq.data;
		return metricsMemoryData;
	} catch (error) {
		console.error(`Failed to get metrics for ${nodes}:`, error.message);
		return;
	}
}
async function getMemoryCPUFromObservabilityService(nodes) {
	try {
		const metricsCPUReq = await axios.get(`${OBSERVABILITY_SERVICE_URL}/metrics/node-cpu?nodes=${nodes}`);
		const metricsCPUData = await metricsCPUReq.data;
		return metricsCPUData;
	} catch (error) {
		console.error(`Failed to get metrics for ${nodes}:`, error.message);
		return;
	}
}

async function getActivePodsObservabilityService(nodes) {
	try {
		const metricsCPUReq = await axios.get(`${OBSERVABILITY_SERVICE_URL}/metrics/node-active-pods?nodes=${nodes}`);
		const metricsCPUData = await metricsCPUReq.data;
		return metricsCPUData;
	} catch (error) {
		console.error(`Failed to get metrics for ${nodes}:`, error.message);
		return;
	}
}

async function getBestNodeFromRLModel(metricsPayload) {
	try {
	  const response = await axios.post(RL_MODEL_URL, metricsPayload, {
		headers: { "Content-Type": "application/json" }
	  });
	  return response.data.scheduled_node;
	} catch (err) {
	  console.error("RL model scheduling failed:", err.message);
	  return null;
	}
  }

module.exports = {
    getMemoryMetricsFromObservabilityService,
	getMemoryCPUFromObservabilityService,
	getActivePodsObservabilityService,
	getBestNodeFromRLModel
};
