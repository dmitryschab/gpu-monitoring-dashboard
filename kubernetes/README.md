# Kubernetes Manifests for GPU Monitoring Dashboard

This directory contains Kubernetes manifests for deploying the GPU Monitoring Dashboard with automated batch analytics.

## Quick Commands

### Deploy Everything
```bash
./deploy.sh
```

### Build Images
```bash
./build-images.sh
```

### Push Images
```bash
./push-images.sh
```

### Undeploy
```bash
./undeploy.sh
```

### Trigger Manual Analytics
```bash
kubectl create job -n gpu-monitoring \
  --from=cronjob/gpu-batch-analytics \
  manual-run-$(date +%s)
```

### View Analytics Logs
```bash
# Get latest job
JOB=$(kubectl get jobs -n gpu-monitoring --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.name}')

# View logs
kubectl logs -n gpu-monitoring job/$JOB -f
```

### Check CronJob Schedule
```bash
kubectl get cronjob -n gpu-monitoring
```

### Access Grafana
```bash
kubectl port-forward -n gpu-monitoring svc/grafana 3000:3000
# Open http://localhost:3000
```

## Manifest Files

| File | Description |
|------|-------------|
| `00-namespace.yaml` | Creates gpu-monitoring namespace |
| `01-zookeeper.yaml` | Zookeeper for Kafka |
| `02-kafka.yaml` | Kafka message broker |
| `03-hadoop.yaml` | Hadoop HDFS (NameNode + DataNode) |
| `04-spark.yaml` | Spark cluster (Master + Workers) |
| `05-influxdb.yaml` | InfluxDB time-series database |
| `06-grafana.yaml` | Grafana dashboard |
| `07-batch-analytics-cronjob.yaml` | **Daily analytics CronJob** |
| `08-persistent-volumes.yaml` | Persistent storage claims |
| `09-configmaps.yaml` | Configuration data |

## CronJob Details

- **Schedule**: Daily at 2:00 AM (UTC)
- **Concurrency**: Forbid (no concurrent runs)
- **Backoff**: 2 retries on failure
- **Timeout**: 2 hours max runtime
- **History**: Keeps last 3 successful and 3 failed jobs

### Modify Schedule

Edit `07-batch-analytics-cronjob.yaml`:

```yaml
spec:
  schedule: "0 2 * * *"  # Change this line
```

Examples:
- `"0 */6 * * *"` - Every 6 hours
- `"0 2,14 * * *"` - 2 AM and 2 PM daily
- `"0 2 * * 0"` - Weekly on Sundays

## Storage Requirements

- **NameNode**: 10 Gi
- **DataNode**: 50 Gi
- **InfluxDB**: 20 Gi
- **Grafana**: 5 Gi
- **Spark Jobs**: 5 Gi

**Total**: ~90 Gi

## Resource Requirements

### Per Component

| Component | CPU Request | Memory Request | CPU Limit | Memory Limit |
|-----------|-------------|----------------|-----------|--------------|
| Analytics Job | 1 core | 2 Gi | 2 cores | 4 Gi |
| Spark Master | 1 core | 1 Gi | 2 cores | 2 Gi |
| Spark Worker | 2 cores | 2 Gi | 4 cores | 4 Gi |
| InfluxDB | 1 core | 2 Gi | 2 cores | 4 Gi |
| Grafana | 0.5 cores | 512 Mi | 1 core | 1 Gi |

## Customization

### Change Analytics Parameters

Edit `09-configmaps.yaml`:

```yaml
data:
  HDFS_INPUT_PATH: "/gpu-metrics"
  HDFS_OUTPUT_PATH: "/gpu-analytics"
  TEMP_SPIKE_THRESHOLD: "5.0"  # Modify thresholds
```

Apply:
```bash
kubectl apply -f 09-configmaps.yaml
```

### Scale Spark Workers

```bash
kubectl scale deployment -n gpu-monitoring spark-worker --replicas=4
```

## Monitoring

### Check All Pods
```bash
kubectl get pods -n gpu-monitoring
```

### Check CronJob Status
```bash
kubectl get cronjob -n gpu-monitoring gpu-batch-analytics -o wide
```

### View Recent Jobs
```bash
kubectl get jobs -n gpu-monitoring --sort-by=.metadata.creationTimestamp
```

### Check Logs
```bash
kubectl logs -n gpu-monitoring <pod-name>
```

## Troubleshooting

### Analytics Job Failed

```bash
# Get job name
kubectl get jobs -n gpu-monitoring

# Describe job
kubectl describe job -n gpu-monitoring <job-name>

# Get pod logs
kubectl logs -n gpu-monitoring <pod-name>
```

### Storage Issues

```bash
# Check PVC status
kubectl get pvc -n gpu-monitoring

# Describe PVC
kubectl describe pvc -n gpu-monitoring <pvc-name>
```

### Network Issues

```bash
# Check services
kubectl get svc -n gpu-monitoring

# Test connectivity
kubectl exec -n gpu-monitoring <pod-name> -- curl http://influxdb:8086/health
```

## Security Notes

**For Production:**

1. Change default passwords in manifests
2. Use Kubernetes Secrets instead of plaintext
3. Enable RBAC
4. Use NetworkPolicies
5. Enable TLS for services
6. Use private container registry

## See Also

- [Full Deployment Guide](../KUBERNETES_DEPLOYMENT.md)
- [Architecture Documentation](../ARCHITECTURE.md)
- [Analytics Guide](../LONG_TERM_ANALYTICS_GUIDE.md)
