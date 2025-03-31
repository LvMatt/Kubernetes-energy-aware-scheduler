@echo off
if "%1"=="delete" (
    kubectl delete -f ./plugins/config/scheduler-config-configmap.yaml
    kubectl delete -f ./plugins/config/rbac.yaml
    kubectl delete -f ./middleware/config/kuberlbridge-service.yaml
) else (
    kubectl apply -f ./plugins/config/scheduler-config-configmap.yaml
    kubectl apply -f ./plugins/config/rbac.yaml
    kubectl apply -f ./middleware/config/kuberlbridge-service.yaml
)