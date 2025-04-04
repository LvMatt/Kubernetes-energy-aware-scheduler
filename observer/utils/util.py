def get_available_nodes():
    nodes = query_prometheus('group(kube_node_info) by (node)')
    return [n["metric"]["node"] for n in nodes] if nodes else []

def get_scrape_targets():
    targets = query_prometheus('up{job="node-exporter"}')
    return [t["metric"]["instance"] for t in targets] if targets else []

__all__ = ['get_available_nodes', 'get_scrape_targets']
