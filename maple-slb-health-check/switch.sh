#!/bin/bash

export KUBECONFIG=~/.kube/config.3d
#for c in ashburn-prod chicago-prod hillsboro-prod; do
for c in ashburn-prod; do
  kubectl delete ingress/mapleapi-staging-hc-ingress -n maple-staging --context ${c};
  kubectl delete ingress/mapleui-staging-hc-ingress -n maple-staging --context ${c};
  kubectl apply -f AS --context ${c}
done
