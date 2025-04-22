kubectl drain energy-aware-k8-cluster-worker --ignore-daemonsets --delete-emptydir-data
kubectl drain energy-aware-k8-cluster-worker2 --ignore-daemonsets --delete-emptydir-data
kubectl drain energy-aware-k8-cluster-worker3 --ignore-daemonsets --delete-emptydir-data


kubectl uncordon energy-aware-k8-cluster-worker
kubectl uncordon energy-aware-k8-cluster-worker2
kubectl uncordon energy-aware-k8-cluster-worker3