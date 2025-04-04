const axios = require("axios");
const OBSERVABILITY_SERVICE_URL = 'http://127.0.0.1:5001'


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


module.exports = {
    getMemoryMetricsFromObservabilityService,
	getMemoryCPUFromObservabilityService,
	getActivePodsObservabilityService
};
