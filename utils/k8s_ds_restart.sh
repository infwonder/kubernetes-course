#!/bin/bash

# Usage: $0 {daemonset_name} {namespace}
# KUBECONFIG needs to be set and make sure kubectl is in $PATH

DS=$1
NAMESPACE=${2:-default}

if [ "x${DS}" == "x" ]; then
  echo "please provide DS name";
  exit 1;
fi

kubectl -n ${NAMESPACE} patch daemonset ${DS} -p '{"spec": {"template": {"spec": {"nodeSelector": {"non-existing": "true"}}}}}'
sleep 3
kubectl -n ${NAMESPACE} patch daemonset ${DS} --type json -p='[{"op": "remove", "path": "/spec/template/spec/nodeSelector/non-existing"}]'

exit 0
