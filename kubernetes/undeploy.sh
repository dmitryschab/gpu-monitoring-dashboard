#!/bin/bash

# Remove GPU Monitoring Dashboard from Kubernetes
set -e

echo "Removing GPU Monitoring Dashboard from Kubernetes..."

# Delete in reverse order
kubectl delete -f kubernetes/07-batch-analytics-cronjob.yaml --ignore-not-found=true
kubectl delete -f kubernetes/06-grafana.yaml --ignore-not-found=true
kubectl delete -f kubernetes/05-influxdb.yaml --ignore-not-found=true
kubectl delete -f kubernetes/04-spark.yaml --ignore-not-found=true
kubectl delete -f kubernetes/03-hadoop.yaml --ignore-not-found=true
kubectl delete -f kubernetes/02-kafka.yaml --ignore-not-found=true
kubectl delete -f kubernetes/01-zookeeper.yaml --ignore-not-found=true
kubectl delete -f kubernetes/09-configmaps.yaml --ignore-not-found=true
kubectl delete -f kubernetes/08-persistent-volumes.yaml --ignore-not-found=true

echo ""
echo "WARNING: The following command will delete the namespace and ALL data:"
echo "  kubectl delete -f kubernetes/00-namespace.yaml"
echo ""
read -p "Do you want to delete the namespace? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    kubectl delete -f kubernetes/00-namespace.yaml
    echo "Namespace deleted."
else
    echo "Namespace preserved."
fi

echo "Undeployment complete!"
