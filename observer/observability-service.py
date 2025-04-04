from flask import Flask, jsonify, request
from utils.util import get_available_nodes, get_scrape_targets

import requests

app = Flask(__name__)

# Testing URL
PROMETHEUS_URL = "http://127.0.0.1:9090/api/v1/query"

# Production URL
#PROMETHEUS_URL = "http://prometheus-server.monitoring.svc.cluster.local:9090/api/v1/query"

def query_prometheus(query):
    try:
        response = requests.get(PROMETHEUS_URL, params={'query': query}, timeout=5)
        response.raise_for_status() 
        data = response.json()
        if data["status"] == "error":
            print("Prometheus Error:", data["error"])
            return {"error": data["error"]}
            
        return data.get("data", {}).get("result", [])
    except Exception as e:
        print("Request Failed:", str(e))
        return {"error": str(e)}
    
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


@app.route('/metrics/node-memory', methods=['GET'])
def get_node_memory():
    node_name = request.args.get('node')
    if not node_name:
        return jsonify({"error": "Missing 'node' parameter"}), 400

    node_info = query_prometheus(f'kube_node_info{{node="{node_name}"}}')
    if not node_info or isinstance(node_info, dict):
        return jsonify({
            "error": f"Node {node_name} not found in cluster",
            "available_nodes": get_available_nodes()
        }), 404

    instance_ip = node_info[0]["metric"]["internal_ip"]
    instance_label = f"{instance_ip}:9100"

    # Get total memory
    total_mem_result = query_prometheus(
        f'node_memory_MemTotal_bytes{{instance="{instance_label}"}}'
    )
    if not total_mem_result or isinstance(total_mem_result, dict):
        return jsonify({"error": "Could not retrieve total memory"}), 500
    total_memory = float(total_mem_result[0]["value"][1])

    # Get available memory
    avail_mem_result = query_prometheus(
        f'node_memory_MemAvailable_bytes{{instance="{instance_label}"}}'
    )
    if not avail_mem_result or isinstance(avail_mem_result, dict):
        return jsonify({"error": "Could not retrieve available memory"}), 500
    available_memory = float(avail_mem_result[0]["value"][1])

    used_memory = total_memory - available_memory
    percent_used = (used_memory / total_memory) * 100

    return jsonify({
        "node": node_name,
        "instance": instance_ip,
        "memory": {
            "total_bytes": total_memory,
            "available_bytes": available_memory,
            "used_bytes": used_memory,
            "used_percent": round(percent_used, 2)
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)