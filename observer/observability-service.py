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
    nodes_param = request.args.get('nodes')
    if not nodes_param:
        return jsonify({"error": "Missing 'nodes' parameter"}), 400

    node_names = nodes_param.split(",")
    results = []

    for node_name in node_names:
        node_info = query_prometheus(f'kube_node_info{{node="{node_name}"}}')
        if not node_info or isinstance(node_info, dict):
            results.append({
                "node": node_name,
                "error": "Node not found"
            })
            continue

        instance_ip = node_info[0]["metric"]["internal_ip"]
        instance_label = f"{instance_ip}:9100"

        total_result = query_prometheus(f'node_memory_MemTotal_bytes{{instance="{instance_label}"}}')
        avail_result = query_prometheus(f'node_memory_MemAvailable_bytes{{instance="{instance_label}"}}')

        if not total_result or not avail_result or isinstance(total_result, dict) or isinstance(avail_result, dict):
            results.append({
                "node": node_name,
                "error": "Memory metrics not found"
            })
            continue

        total = float(total_result[0]["value"][1])
        available = float(avail_result[0]["value"][1])
        used = total - available
        percent = (used / total) * 100

        results.append({
            "node": node_name,
            "instance": instance_ip,
            "memory": {
                "total_bytes": total,
                "available_bytes": available,
                "used_bytes": used,
                "used_percent": round(percent, 2)
            }
        })

    return jsonify(results)

@app.route('/metrics/node-cpu', methods=['GET'])
def get_node_cpu():
    nodes_param = request.args.get('nodes')
    if not nodes_param:
        return jsonify({"error": "Missing 'nodes' parameter"}), 400

    node_names = nodes_param.split(",")
    results = []

    for node_name in node_names:
        node_info = query_prometheus(f'kube_node_info{{node="{node_name}"}}')
        if not node_info or isinstance(node_info, dict):
            results.append({
                "node": node_name,
                "error": "Node not found"
            })
            continue

        instance_ip = node_info[0]["metric"]["internal_ip"]
        instance_label = f"{instance_ip}:9100"

        cpu_cores_result = query_prometheus(
            f'count(count by (cpu) (node_cpu_seconds_total{{instance="{instance_label}"}}))'
        )

        # Get CPU usage (100 - idle rate avg over 1m)
        cpu_usage_result = query_prometheus(
            f'100 - (avg by (instance) (rate(node_cpu_seconds_total{{mode="idle", instance="{instance_label}"}}[1m])) * 100)'
        )

        if not cpu_cores_result or not cpu_usage_result or isinstance(cpu_cores_result, dict) or isinstance(cpu_usage_result, dict):
            results.append({
                "node": node_name,
                "error": "CPU metrics not found"
            })
            continue

        cpu_cores = int(float(cpu_cores_result[0]["value"][1]))
        cpu_used_percent = float(cpu_usage_result[0]["value"][1])

        results.append({
            "node": node_name,
            "instance": instance_ip,
            "cpu": {
                "cores": cpu_cores,
                "used_percent": round(cpu_used_percent, 2)
            }
        })

    return jsonify(results)


@app.route('/metrics/node-active-pods', methods=['GET'])
def get_node_active_pods():
    nodes_param = request.args.get('nodes')
    if not nodes_param:
        return jsonify({"error": "Missing 'nodes' parameter"}), 400

    node_names = [n.strip() for n in nodes_param.split(",")] 
    results = []

    for node_name in node_names:
        node_info = query_prometheus(f'kube_node_info{{node="{node_name}"}}')
       
        pod_query = (
            f'count(kube_pod_status_phase{{phase="Running"}} '
            f'* on (namespace, pod) group_left(node) '
            f'kube_pod_info{{node="{node_name}"}})'
        )

        pod_count_result = query_prometheus(pod_query)
        if not pod_count_result or isinstance(pod_count_result, dict):
            results.append({
                "node": node_name,
                "error": "Pod metrics not found"
            })
            continue

        pod_count = int(float(pod_count_result[0]["value"][1]))
        instance_ip = node_info[0]["metric"]["internal_ip"]

        results.append({
            "node": node_name,
            "instance": instance_ip,
            "active_pods": pod_count
        })

    return jsonify(results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)