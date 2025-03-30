@echo off
set action=%1

if "%action%"=="delete" (
    echo Deleting Kubernetes deployments...
    kubectl delete -f .\middleware\deploy\kuberlbridge-deployment.yaml -n kube-system
    kubectl delete -f .\plugins\deploy\energy-scheduler-deployment.yaml -n kube-system
    kubectl delete -f .\plugins\config\test-pod.yaml
) else (
    echo Applying Kubernetes deployments...
    kubectl apply -f .\middleware\deploy\kuberlbridge-deployment.yaml -n kube-system
    kubectl apply -f .\plugins\deploy\energy-scheduler-deployment.yaml -n kube-system
    kubectl apply -f .\plugins\config\test-pod.yaml
)
