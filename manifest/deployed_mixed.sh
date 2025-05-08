#!/bin/bash

# Mixed deployment: 30 app pods + 50 job pods
# Deploy pattern: 2 jobs, then 1 app (25 iterations) + 5 extra apps at the end

delete_job_after_completion() {
  local job_name=$1
  while true; do
    phase=$(kubectl get pod "$job_name" -o jsonpath='{.status.phase}' 2>/dev/null)
    if [[ "$phase" == "Succeeded" || "$phase" == "Failed" ]]; then
      echo "Job $job_name finished with status: $phase. Deleting..."
      kubectl delete pod "$job_name" --ignore-not-found
      break
    fi
    sleep 5
  done
}

app_count=0
job_count=0
total_iterations=25
extra_apps=5

echo "🚀 Starting stress-ng mixed deployment..."

for i in $(seq 1 $total_iterations); do
  # 2 Jobs
  for j in 1 2; do
    ((job_count++))
    job_name="job-pod-$job_count"
    cpu_millicores=$((25 + RANDOM % 50))    # 25–75m
    mem_mib=$((30 + RANDOM % 50))          # 30–80Mi

    cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: $job_name
  namespace: kube-experiments
  labels:
    app: job
spec:
  schedulerName: energy-scheduler
  restartPolicy: Never
  containers:
  - name: $job_name-container
    image: ubuntu:22.04
    command: ["/bin/bash", "-c"]
    args:
      - apt-get update && \
        apt-get install -y --no-install-recommends stress-ng && \
        stress-ng --vm 1 --vm-bytes ${mem_mib}M --vm-keep --timeout 60
    resources:
      requests:
        cpu: "${cpu_millicores}m"
        memory: "${mem_mib}Mi"
      limits:
        cpu: "${cpu_millicores}m"
        memory: "${mem_mib}Mi"
EOF

    echo "✅ Deployed job: $job_name"
    delete_job_after_completion "$job_name" &
  done

  # 1 App
  ((app_count++))
  app_name="app-pod-$app_count"
  cpu_millicores=$((50 + RANDOM % 50))     # 50–100m
  mem_mib=$((70 + RANDOM % 30))            # 70–100Mi

  cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: $app_name
  namespace: kube-experiments
  labels:
    app: app
spec:
  schedulerName: energy-scheduler
  restartPolicy: Always
  containers:
  - name: $app_name-container
    image: ubuntu:22.04
    command: ["/bin/bash", "-c"]
    args:
      - apt-get update && \
        apt-get install -y --no-install-recommends stress-ng && \
        stress-ng --vm 1 --vm-bytes ${mem_mib}M --vm-keep --timeout 1800
    resources:
      requests:
        cpu: "${cpu_millicores}m"
        memory: "${mem_mib}Mi"
      limits:
        cpu: "${cpu_millicores}m"
        memory: "${mem_mib}Mi"
EOF

  echo "✅ Deployed app: $app_name"
  sleep 20
done

# Deploy 5 more apps to reach 30 total
for i in $(seq 1 $extra_apps); do
  ((app_count++))
  app_name="app-pod-$app_count"
  cpu_millicores=$((50 + RANDOM % 50))
  mem_mib=$((70 + RANDOM % 30))

  cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: $app_name
  namespace: kube-experiments
  labels:
    app: app
spec:
  schedulerName: energy-scheduler
  restartPolicy: Always
  containers:
  - name: $app_name-container
    image: ubuntu:22.04
    command: ["/bin/bash", "-c"]
    args:
      - apt-get update && \
        apt-get install -y --no-install-recommends stress-ng && \
        stress-ng --vm 1 --vm-bytes ${mem_mib}M --vm-keep --timeout 1800
    resources:
      requests:
        cpu: "${cpu_millicores}m"
        memory: "${mem_mib}Mi"
      limits:
        cpu: "${cpu_millicores}m"
        memory: "${mem_mib}Mi"
EOF

  echo "✅ Deployed extra app: $app_name"
  sleep 20
done

wait
echo "🎉 Deployment complete. All job pods will self-delete after completion."
