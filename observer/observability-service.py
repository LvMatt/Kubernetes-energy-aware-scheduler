from flask import Flask, jsonify
import requests

app = Flask(__name__)

PROMETHEUS_URL = "http://prometheus-server.monitoring.svc.cluster.local:9090/api/v1/query"

def query_prometheus(query):
    response = requests.get(PROMETHEUS_URL, params={'query': query})
    data = response.json()
    return data["data"]["result"]

@app.route('/metrics/cpu', methods=['GET'])
def get_cpu_usage():
    return jsonify(query_prometheus("rate(node_cpu_seconds_total[5m])"))

@app.route('/metrics/memory', methods=['GET'])
def get_memory_usage():
    return jsonify(query_prometheus("node_memory_Active_bytes"))

@app.route('/metrics/energy', methods=['GET'])
def get_energy_consumption():
    return jsonify({"message": "Energy metrics not available in default Node Exporter."})

@app.route('/metrics/all', methods=['GET'])
def get_all_metrics():
    return jsonify({
        "cpu": query_prometheus("rate(node_cpu_seconds_total[5m])"),
        "memory": query_prometheus("node_memory_Active_bytes"),
        "energy": "N/A"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)