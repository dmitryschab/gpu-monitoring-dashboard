# Kubernetes Deployment Guide

This guide explains how to deploy the GPU Monitoring Dashboard to a Kubernetes cluster with automated daily batch analytics.

## Overview

The Kubernetes deployment includes:
- **CronJob**: Runs batch analytics daily at 2 AM
- **StatefulSets**: For Hadoop, InfluxDB, and Grafana (with persistent storage)
- **Deployments**: For Kafka, Zookeeper, Spark
- **Services**: For inter-component communication
- **PersistentVolumeClaims**: For data persistence

## Prerequisites

1. **Kubernetes Cluster**: Running cluster (minikube, GKE, EKS, AKS, or on-premise)
2. **kubectl**: Installed and configured
3. **Docker**: For building images
4. **Storage Class**: Default storage class available (or modify `storageClassName` in manifests)

## Quick Start

### 1. Build Docker Images

```bash
cd gpu-monitoring-dashboard

# Build all images
./kubernetes/build-images.sh

# Or set custom registry
export DOCKER_REGISTRY=myregistry.io/myuser
export VERSION=1.0.0
./kubernetes/build-images.sh
```

### 2. Push Images to Registry

```bash
# Push to your container registry
./kubernetes/push-images.sh

# Or manually
docker push myregistry.io/myuser/gpu-monitoring/kafka-producer:1.0.0
docker push myregistry.io/myuser/gpu-monitoring/influxdb-consumer:1.0.0
docker push myregistry.io/myuser/gpu-monitoring/batch-analytics:1.0.0
```

### 3. Update Image References

Edit [kubernetes/07-batch-analytics-cronjob.yaml](kubernetes/07-batch-analytics-cronjob.yaml) and update:

```yaml
containers:
  - name: batch-analytics
    image: myregistry.io/myuser/gpu-monitoring/batch-analytics:1.0.0
```

### 4. Deploy to Kubernetes

```bash
# Deploy everything
./kubernetes/deploy.sh
```

### 5. Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n gpu-monitoring

# Check CronJob is scheduled
kubectl get cronjob -n gpu-monitoring

# Check services
kubectl get svc -n gpu-monitoring
```

## Architecture

### Components

| Component | Type | Purpose |
|-----------|------|---------|
| Zookeeper | Deployment | Kafka coordination |
| Kafka | Deployment | Message broker |
| Hadoop NameNode | StatefulSet | HDFS metadata |
| Hadoop DataNode | StatefulSet | HDFS data storage |
| Spark Master | Deployment | Spark cluster master |
| Spark Worker | Deployment (2 replicas) | Spark executors |
| InfluxDB | StatefulSet | Time-series database |
| Grafana | StatefulSet | Visualization dashboard |
| Batch Analytics | CronJob | Daily analytics job |

### Storage

| PVC | Size | Usage |
|-----|------|-------|
| namenode-data | 10Gi | HDFS NameNode metadata |
| datanode-data | 50Gi | HDFS raw data storage |
| influxdb-data | 20Gi | InfluxDB metrics |
| grafana-data | 5Gi | Grafana dashboards |
| spark-jobs-pvc | 5Gi | Spark job files |

## CronJob Configuration

The batch analytics runs **daily at 2 AM** (UTC).

### CronJob Specification

```yaml
schedule: "0 2 * * *"  # Daily at 2 AM
concurrencyPolicy: Forbid  # Don't run concurrent jobs
successfulJobsHistoryLimit: 3
failedJobsHistoryLimit: 3
```

### Modify Schedule

Edit [kubernetes/07-batch-analytics-cronjob.yaml](kubernetes/07-batch-analytics-cronjob.yaml):

```yaml
# Run every 6 hours
schedule: "0 */6 * * *"

# Run twice daily (2 AM and 2 PM)
schedule: "0 2,14 * * *"

# Run weekly on Sundays at 2 AM
schedule: "0 2 * * 0"
```

Cron format: `minute hour day-of-month month day-of-week`

## Manual Job Execution

### Trigger Analytics On-Demand

```bash
# Create a manual job from the CronJob
kubectl create job -n gpu-monitoring \
  --from=cronjob/gpu-batch-analytics \
  gpu-batch-analytics-manual-$(date +%s)
```

### Check Job Status

```bash
# List all jobs
kubectl get jobs -n gpu-monitoring

# Get job details
kubectl describe job -n gpu-monitoring gpu-batch-analytics-manual-1234567890

# View job logs
kubectl logs -n gpu-monitoring job/gpu-batch-analytics-manual-1234567890
```

### Delete Completed Jobs

```bash
# Delete a specific job
kubectl delete job -n gpu-monitoring gpu-batch-analytics-manual-1234567890

# Delete all completed jobs
kubectl delete jobs -n gpu-monitoring --field-selector status.successful=1
```

## Accessing Services

### Grafana Dashboard

```bash
# Port forward to local machine
kubectl port-forward -n gpu-monitoring svc/grafana 3000:3000

# Open in browser
open http://localhost:3000
```

**Default credentials:**
- Username: `admin`
- Password: `admin`

### Spark UI

```bash
# Port forward Spark Master UI
kubectl port-forward -n gpu-monitoring svc/spark-master 8080:8080

# Open in browser
open http://localhost:8080
```

### Hadoop NameNode UI

```bash
# Port forward NameNode UI
kubectl port-forward -n gpu-monitoring svc/namenode 9870:9870

# Open in browser
open http://localhost:9870
```

### InfluxDB UI

```bash
# Port forward InfluxDB
kubectl port-forward -n gpu-monitoring svc/influxdb 8086:8086

# Open in browser
open http://localhost:8086
```

## Monitoring and Troubleshooting

### Check CronJob Status

```bash
# View CronJob details
kubectl describe cronjob -n gpu-monitoring gpu-batch-analytics

# Check last schedule time
kubectl get cronjob -n gpu-monitoring gpu-batch-analytics -o yaml | grep lastScheduleTime
```

### View Logs

```bash
# Get the latest job
JOB_NAME=$(kubectl get jobs -n gpu-monitoring --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.name}')

# View logs
kubectl logs -n gpu-monitoring job/$JOB_NAME

# Follow logs
kubectl logs -n gpu-monitoring job/$JOB_NAME -f
```

### Common Issues

#### CronJob Not Running

```bash
# Check if CronJob is suspended
kubectl get cronjob -n gpu-monitoring gpu-batch-analytics -o yaml | grep suspend

# Resume if suspended
kubectl patch cronjob -n gpu-monitoring gpu-batch-analytics -p '{"spec":{"suspend":false}}'
```

#### Job Failed

```bash
# Get failed job details
kubectl describe job -n gpu-monitoring <job-name>

# Check pod events
kubectl get events -n gpu-monitoring --sort-by='.lastTimestamp' | grep <job-name>

# Check pod logs
kubectl logs -n gpu-monitoring <pod-name>
```

#### Storage Issues

```bash
# Check PVC status
kubectl get pvc -n gpu-monitoring

# Check PV status
kubectl get pv

# Describe PVC for details
kubectl describe pvc -n gpu-monitoring spark-jobs-pvc
```

## Scaling

### Scale Spark Workers

```bash
# Scale to 4 workers
kubectl scale deployment -n gpu-monitoring spark-worker --replicas=4

# Or edit the deployment
kubectl edit deployment -n gpu-monitoring spark-worker
```

### Adjust Resource Limits

Edit [kubernetes/07-batch-analytics-cronjob.yaml](kubernetes/07-batch-analytics-cronjob.yaml):

```yaml
resources:
  requests:
    memory: "4Gi"  # Increase from 2Gi
    cpu: "2"       # Increase from 1
  limits:
    memory: "8Gi"  # Increase from 4Gi
    cpu: "4"       # Increase from 2
```

Apply changes:

```bash
kubectl apply -f kubernetes/07-batch-analytics-cronjob.yaml
```

## Configuration

### Environment Variables

Edit [kubernetes/09-configmaps.yaml](kubernetes/09-configmaps.yaml):

```yaml
data:
  HDFS_INPUT_PATH: "/gpu-metrics"
  HDFS_OUTPUT_PATH: "/gpu-analytics"
  TEMP_SPIKE_THRESHOLD: "10.0"  # Change threshold
  HIGH_TEMP_THRESHOLD: "85.0"
```

Apply changes:

```bash
kubectl apply -f kubernetes/09-configmaps.yaml
```

### Update Grafana Configuration

```bash
# Edit ConfigMap
kubectl edit configmap -n gpu-monitoring grafana-provisioning

# Or update the file and apply
kubectl apply -f kubernetes/09-configmaps.yaml

# Restart Grafana to pick up changes
kubectl rollout restart statefulset -n gpu-monitoring grafana
```

## Backup and Restore

### Backup HDFS Data

```bash
# Create a backup job
kubectl exec -n gpu-monitoring namenode-0 -- \
  hdfs dfs -get /gpu-metrics /backup/gpu-metrics-$(date +%Y%m%d)
```

### Backup InfluxDB

```bash
# Backup InfluxDB data
kubectl exec -n gpu-monitoring influxdb-0 -- \
  influx backup /backup/influxdb-$(date +%Y%m%d)
```

### Restore from Backup

```bash
# Restore HDFS
kubectl exec -n gpu-monitoring namenode-0 -- \
  hdfs dfs -put /backup/gpu-metrics-20251015 /gpu-metrics

# Restore InfluxDB
kubectl exec -n gpu-monitoring influxdb-0 -- \
  influx restore /backup/influxdb-20251015
```

## Cleanup

### Remove Deployment (Keep Data)

```bash
./kubernetes/undeploy.sh
# Select 'N' when asked about namespace deletion
```

### Complete Removal (Including Data)

```bash
./kubernetes/undeploy.sh
# Select 'Y' when asked about namespace deletion

# Or manually
kubectl delete namespace gpu-monitoring
```

## Production Considerations

### 1. Use Secrets for Credentials

Replace hardcoded passwords with Kubernetes Secrets:

```bash
# Create secret
kubectl create secret generic influxdb-credentials \
  -n gpu-monitoring \
  --from-literal=admin-password='your-secure-password' \
  --from-literal=admin-token='your-secure-token'

# Reference in deployment
env:
  - name: DOCKER_INFLUXDB_INIT_PASSWORD
    valueFrom:
      secretKeyRef:
        name: influxdb-credentials
        key: admin-password
```

### 2. Configure Persistent Storage

For production, use appropriate StorageClass:

```yaml
storageClassName: fast-ssd  # or your cloud provider's SSD class
```

### 3. Set Resource Requests/Limits

Ensure all pods have appropriate resource limits:

```yaml
resources:
  requests:
    memory: "2Gi"
    cpu: "1"
  limits:
    memory: "4Gi"
    cpu: "2"
```

### 4. Enable Monitoring

Add Prometheus monitoring:

```bash
# Install Prometheus Operator
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml

# Add ServiceMonitor for your pods
```

### 5. Configure Backups

Set up automated backups using Velero or cloud-native backup solutions.

### 6. Use LoadBalancer/Ingress

For Grafana access:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: gpu-monitoring
spec:
  type: LoadBalancer  # or use Ingress
  ports:
    - port: 3000
```

## Advanced Usage

### Custom Analytics Script

1. Modify [spark-jobs/batch_analytics.py](spark-jobs/batch_analytics.py)
2. Rebuild the Docker image
3. Push to registry
4. Update CronJob to use new image version

### Multiple CronJobs

Create separate CronJobs for different analytics:

```yaml
# Weekly summary job
schedule: "0 3 * * 0"  # Sundays at 3 AM

# Monthly reports
schedule: "0 4 1 * *"  # 1st of month at 4 AM
```

### Integration with CI/CD

Add to your CI/CD pipeline:

```bash
# .github/workflows/deploy.yml
- name: Deploy to Kubernetes
  run: |
    ./kubernetes/build-images.sh
    ./kubernetes/push-images.sh
    ./kubernetes/deploy.sh
```

## Support

For issues or questions:
1. Check logs: `kubectl logs -n gpu-monitoring <pod-name>`
2. Check events: `kubectl get events -n gpu-monitoring`
3. Review [ARCHITECTURE.md](ARCHITECTURE.md)
4. Review [LONG_TERM_ANALYTICS_GUIDE.md](LONG_TERM_ANALYTICS_GUIDE.md)

## References

- [Kubernetes CronJobs](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
- [Spark on Kubernetes](https://spark.apache.org/docs/latest/running-on-kubernetes.html)
- [HDFS Architecture](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html)
