@echo off
REM GPU Monitoring Dashboard Startup Script for Windows

echo ======================================
echo GPU Monitoring Dashboard Setup
echo ======================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Check if docker-compose.yml exists
if not exist "docker-compose.yml" (
    echo Error: docker-compose.yml not found. Run this script from the project root.
    pause
    exit /b 1
)

echo [OK] Found docker-compose.yml
echo.

REM Start services
echo Starting services...
echo This may take a few minutes on first run...
docker-compose up -d

echo.
echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check service status
echo.
echo Checking service status...

docker-compose ps | findstr "zookeeper" >nul && (
    echo [OK] zookeeper is running
) || (
    echo [ERROR] zookeeper is not running
)

docker-compose ps | findstr "kafka" >nul && (
    echo [OK] kafka is running
) || (
    echo [ERROR] kafka is not running
)

docker-compose ps | findstr "namenode" >nul && (
    echo [OK] namenode is running
) || (
    echo [ERROR] namenode is not running
)

docker-compose ps | findstr "spark-master" >nul && (
    echo [OK] spark-master is running
) || (
    echo [ERROR] spark-master is not running
)

docker-compose ps | findstr "influxdb" >nul && (
    echo [OK] influxdb is running
) || (
    echo [ERROR] influxdb is not running
)

docker-compose ps | findstr "grafana" >nul && (
    echo [OK] grafana is running
) || (
    echo [ERROR] grafana is not running
)

REM Wait for Kafka to be fully ready
echo.
echo Waiting for Kafka to be fully ready...
timeout /t 15 /nobreak >nul

REM Create Kafka topic
echo.
echo Creating Kafka topic 'gpu-metrics'...
docker exec kafka kafka-topics --create --if-not-exists --topic gpu-metrics --bootstrap-server localhost:9093 --partitions 1 --replication-factor 1 2>nul

echo [OK] Kafka topic created
echo.

REM Display access URLs
echo ======================================
echo Services are ready!
echo ======================================
echo.
echo Access the following UIs:
echo   * Grafana:        http://localhost:3000 (admin/admin)
echo   * InfluxDB:       http://localhost:8086 (admin/adminpassword)
echo   * Spark Master:   http://localhost:8080
echo   * Hadoop HDFS:    http://localhost:9870
echo.
echo ======================================
echo Next Steps:
echo ======================================
echo.
echo 1. Copy your GPU-Z log file to the data\ directory
echo.
echo 2. Install Python dependencies:
echo    cd kafka-producer
echo    pip install -r requirements.txt
echo.
echo 3. Start the Kafka producer (in a new terminal):
echo    cd kafka-producer
echo    python gpuz_producer.py --file "..\data\GPU-Z Sensor Log.txt" --speed 1.0 --loop
echo.
echo 4. Start the InfluxDB consumer (in another terminal):
echo    cd kafka-producer
echo    python influxdb_consumer.py
echo.
echo 5. Open Grafana and create your dashboard:
echo    http://localhost:3000
echo.
echo ======================================
echo To stop all services:
echo   docker-compose down
echo ======================================
echo.
pause
