#!/bin/bash

mkdir -p temp_pods

# Split the multi-document YAML file into separate files
awk -v RS='---' '
    /kind:[[:space:]]*Pod/ {
        file = sprintf("temp_pods/pod_%03d.yaml", ++i)
        print "---" > file
        print $0 >> file
    }
' apps_pods.yaml

# Delete only the Pod resources
for pod_file in temp_pods/*.yaml; do
  echo "Deleting $pod_file..."
  kubectl delete -f "$pod_file"
  sleep 3
done

# Optional: cleanup
rm -r temp_pods
