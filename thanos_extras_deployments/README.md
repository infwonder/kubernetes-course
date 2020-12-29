Thanos sidecar deployment is done via rancher-modified kube-prometheus stack chart:

...
prometheus:
...
  prometheusSpec:
...
    thanos:
      image: 'quay.io/thanos/thanos:v0.17.2'
      version: v0.17.2

This test is done on Rancher 2.5 which has revamped their monitoring and utilize on Helm to further generalize component installation and upgrades.

Rancher chart developer github:
 https://github.com/rancher/charts/tree/dev-v2.5-source

References:
 https://thanos.io/tip/thanos/quick-tutorial.md/
 https://github.com/prometheus-operator/prometheus-operator/tree/master/example/thanos
 https://www.metricfire.com/blog/ha-kubernetes-monitoring-using-prometheus-and-thanos/
 https://github.com/prometheus-operator/prometheus-operator/blob/master/Documentation/api.md#thanosspec
 
