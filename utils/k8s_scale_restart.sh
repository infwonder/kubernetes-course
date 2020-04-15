#!/bin/bash

# Usage: $0 {resource_type} {resource_name} {scale_back_count} {namespace}
# KUBECONFIG needs to be set and make sure kubectl is in PATH

TYPE=$1

if [ "x${TYPE}" == "x" ]; then
  echo "Please provides type, either be deployment, replicaset, or statefulset"
  exit 1
fi

NAME=$2

if [ "x${NAME}" == "x" ]; then
  echo "Please provides name of the type"
  exit 2
fi

COUNT=${3:-0}

if [ "${COUNT}" ==  "0" ]; then
  echo "Please provides desire count to scale back"
  exit 3
fi

NAMESPACE=${4:-default}

kubectl scale --replicas=0 -n ${NAMESPACE} ${TYPE}/${NAME}
sleep 3
kubectl scale --replicas=${COUNT} -n ${NAMESPACE} ${TYPE}/${NAME}
