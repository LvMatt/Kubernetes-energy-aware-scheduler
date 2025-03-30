if [ "$1" == "delete" ]; then
	kubectl delete -f ./middleware/deploy/kuberlbridge-deployment.yaml -n kube-system
	kubectl delete -f ./plugins/deploy/energy-scheduler-deployment.yaml -n kube-system
	kubectl delete -f ./plugins/config/test-pod.yaml
else 
	kubectl apply -f ./middleware/deploy/kuberlbridge-deployment.yaml -n kube-system
	kubectl apply -f ./plugins/deploy/energy-scheduler-deployment.yaml -n kube-system
	kubectl apply -f ./plugins/config/test-pod.yaml
fi