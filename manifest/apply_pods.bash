#!/bin/bash

mkdir -p temp_pods

awk -v RS='---' '
    NF {
        file = sprintf("temp_pods/pod_%03d.yaml", ++i)
        print "---" > file
        print $0 >> file
    }
' apps_pods.yaml

for pod_file in temp_pods/*.yaml; do
  echo "Applying $pod_file..."
  kubectl apply -f "$pod_file"
  sleep 5
done

# Optional: cleanup
rm -r temp_pods
