const axios = require("axios");
const OBSERVABILITY_SERVICE_URL = 'http://localhost:5001'


async function getMemoryMetricsFromObservabilityService(nodes) {
	try {
		const metricsMemoryReq = await axios.get(`${OBSERVABILITY_SERVICE_URL}/metrics/node-memory?nodes=${nodes}`);
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


module.exports = {
    getMemoryMetricsFromObservabilityService,
	getMemoryCPUFromObservabilityService
};
