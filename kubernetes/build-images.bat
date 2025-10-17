@echo off
REM Build Docker images for Kubernetes deployment (Windows)

echo Building Docker images for GPU Monitoring Dashboard...
echo.

REM Define image registry (change this to your registry)
set REGISTRY=%DOCKER_REGISTRY%
if "%REGISTRY%"=="" set REGISTRY=localhost:5000

set VERSION=%VERSION%
if "%VERSION%"=="" set VERSION=latest

cd ..

REM Build Kafka Producer image
echo Building kafka-producer image...
docker build -f docker\Dockerfile.kafka-producer -t %REGISTRY%/gpu-monitoring/kafka-producer:%VERSION% .

REM Build InfluxDB Consumer image
echo Building influxdb-consumer image...
docker build -f docker\Dockerfile.influxdb-consumer -t %REGISTRY%/gpu-monitoring/influxdb-consumer:%VERSION% .

REM Build Batch Analytics image
echo Building batch-analytics image...
docker build -f docker\Dockerfile.batch-analytics -t %REGISTRY%/gpu-monitoring/batch-analytics:%VERSION% .

echo.
echo Images built successfully!
echo.
echo To push to registry:
echo   docker push %REGISTRY%/gpu-monitoring/kafka-producer:%VERSION%
echo   docker push %REGISTRY%/gpu-monitoring/influxdb-consumer:%VERSION%
echo   docker push %REGISTRY%/gpu-monitoring/batch-analytics:%VERSION%
echo.
echo Or run: .\kubernetes\push-images.bat
echo.

pause
