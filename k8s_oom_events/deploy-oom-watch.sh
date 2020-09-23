#!/bin/bash

export KUBECONFIG=/Users/ylin020/.kube/config.ch.prod

kubectl create serviceaccount kubernetes-oom-event-generator --namespace=kube-system && \
kubectl create -f cluster-role.yml && \
kubectl create clusterrolebinding cdn:maple:kubernetes-oom-event-generator --clusterrole=kubernetes-oom-event-generator --serviceaccount=kube-system:kubernetes-oom-event-generator && \
kubectl apply -f kubernetes-oom-event-generator.yml 
