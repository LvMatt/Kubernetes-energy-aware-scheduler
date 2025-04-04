const axios = require("axios");
const OBSERVABILITY_SERVICE_URL = 'http://localhost:5001'


async function getNodeMetricsFromObservabilityService(nodes) {
	try {
		const metricsReq = await axios.get(`${OBSERVABILITY_SERVICE_URL}/metrics/node-memory?nodes=${nodes}`);
		const metricsJson = await metricsReq.data;
		return metricsJson;
	} catch (error) {
		console.error(`Failed to get metrics for ${nodes}:`, error.message);
		return;
	}
}

module.exports = {
    getNodeMetricsFromObservabilityService
};
