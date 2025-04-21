if [ "$1" == "delete" ]; then
	kubectl  delete -f ./plugins/config/scheduler-config-configmap.yaml
	kubectl  delete -f ./plugins/config/rbac.yaml
	kubectl  delete -f ./middleware/config/kuberlbridge-service.yaml
	kubectl  delete -f ./observer/config/observer-service.yaml
	kubectl  delete -f ./RL-service/config/rl-scheduler-service.yaml
else
	kubectl  apply -f ./plugins/config/scheduler-config-configmap.yaml
	kubectl  apply -f ./plugins/config/rbac.yaml
	kubectl  apply -f ./middleware/config/kuberlbridge-service.yaml
	kubectl  apply -f ./observer/config/observer-service.yaml
	kubectl  apply -f ./RL-service/config/rl-scheduler-service.yaml
fi