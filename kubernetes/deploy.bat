@echo off
REM Deploy GPU Monitoring Dashboard to Kubernetes (Windows)

echo Deploying GPU Monitoring Dashboard to Kubernetes...
echo.

REM Check if kubectl is available
kubectl version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: kubectl is not installed or not in PATH
    exit /b 1
)

echo Creating namespace...
kubectl apply -f kubernetes\00-namespace.yaml

echo Creating persistent volumes...
kubectl apply -f kubernetes\08-persistent-volumes.yaml

echo Creating ConfigMaps...
kubectl apply -f kubernetes\09-configmaps.yaml

echo Deploying Zookeeper...
kubectl apply -f kubernetes\01-zookeeper.yaml

echo Deploying Kafka...
kubectl apply -f kubernetes\02-kafka.yaml

echo Deploying Hadoop (NameNode and DataNode)...
kubectl apply -f kubernetes\03-hadoop.yaml

echo Deploying Spark (Master and Workers)...
kubectl apply -f kubernetes\04-spark.yaml

echo Deploying InfluxDB...
kubectl apply -f kubernetes\05-influxdb.yaml

echo Deploying Grafana...
kubectl apply -f kubernetes\06-grafana.yaml

echo Deploying Batch Analytics CronJob...
kubectl apply -f kubernetes\07-batch-analytics-cronjob.yaml

echo.
echo Deployment complete!
echo.
echo Checking deployment status...
kubectl get pods -n gpu-monitoring

echo.
echo To view logs:
echo   kubectl logs -n gpu-monitoring ^<pod-name^>
echo.
echo To check CronJob:
echo   kubectl get cronjob -n gpu-monitoring
echo.
echo To manually trigger analytics job:
echo   kubectl create job -n gpu-monitoring --from=cronjob/gpu-batch-analytics gpu-batch-analytics-manual
echo.
echo To access Grafana:
echo   kubectl port-forward -n gpu-monitoring svc/grafana 3000:3000
echo   Then open http://localhost:3000
echo.

pause
