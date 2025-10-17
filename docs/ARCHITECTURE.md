# Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         GPU MONITORING DASHBOARD                         │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│   GPU-Z Logs     │  Your actual GPU-Z sensor log file
│   (CSV format)   │  32+ metrics logged every ~1 second
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                          DATA INGESTION LAYER                             │
├──────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │  Kafka Producer (gpuz_producer.py)                             │     │
│  │  • Parses CSV log files                                        │     │
│  │  • Converts to JSON                                            │     │
│  │  • Publishes to Kafka topic                                    │     │
│  │  • Configurable replay speed                                   │     │
│  └──────────────────────┬─────────────────────────────────────────┘     │
└─────────────────────────┼───────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                       MESSAGE BROKER LAYER                                │
├──────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │  Apache Kafka                                                │        │
│  │  • Topic: gpu-metrics                                        │        │
│  │  • 1 partition, replication factor 1                         │        │
│  │  • Message format: JSON                                      │        │
│  │  • Throughput: ~60-120 messages/minute                       │        │
│  └────────────────┬────────────────┬────────────────────────────┘        │
│                   │                │                                      │
│  ┌────────────────┘                └──────────────────┐                  │
│  │  Zookeeper                                         │                  │
│  │  (Coordination)                                    │                  │
│  └────────────────────────────────────────────────────┘                  │
└──────────────────────┬──────────────────┬────────────────────────────────┘
                       │                  │
          ┌────────────┘                  └─────────────┐
          │                                             │
          ▼                                             ▼
┌────────────────────────┐                  ┌──────────────────────────────┐
│  REAL-TIME PATH        │                  │  BATCH PATH                  │
├────────────────────────┤                  ├──────────────────────────────┤
│                        │                  │                              │
│ ┌──────────────────┐  │                  │  ┌──────────────────────┐   │
│ │ InfluxDB         │  │                  │  │ Spark Streaming      │   │
│ │ Consumer         │  │                  │  │ • Window aggregations│   │
│ │ • Consumes from  │  │                  │  │ • Anomaly detection  │   │
│ │   Kafka          │  │                  │  │ • Real-time alerts   │   │
│ │ • Writes to      │  │                  │  └──────────┬───────────┘   │
│ │   InfluxDB       │  │                  │             │               │
│ └────────┬─────────┘  │                  │             ▼               │
│          │            │                  │  ┌──────────────────────┐   │
│          ▼            │                  │  │ HDFS Storage         │   │
│ ┌──────────────────┐  │                  │  │ • Parquet format     │   │
│ │ InfluxDB         │  │                  │  │ • Compressed         │   │
│ │ • Time-series DB │  │                  │  │ • Historical data    │   │
│ │ • Flux queries   │  │                  │  └──────────┬───────────┘   │
│ │ • Retention      │  │                  │             │               │
│ │   policies       │  │                  │             ▼               │
│ └────────┬─────────┘  │                  │  ┌──────────────────────┐   │
│          │            │                  │  │ Batch Analytics      │   │
│          ▼            │                  │  │ • Daily stats        │   │
│ ┌──────────────────┐  │                  │  │ • Hourly patterns    │   │
│ │ Grafana          │  │                  │  │ • Spike detection    │   │
│ │ • Real-time      │  │                  │  │ • Correlations       │   │
│ │   dashboards     │  │                  │  └──────────────────────┘   │
│ │ • Alerting       │  │                  │                              │
│ │ • Visualizations │  │                  └──────────────────────────────┘
│ └──────────────────┘  │
└────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                                  │
├──────────────────────────────────────────────────────────────────────────┤
│  Web Browsers:                                                            │
│  • Grafana Dashboard     → http://localhost:3000                         │
│  • InfluxDB UI           → http://localhost:8086                         │
│  • Spark UI              → http://localhost:8080                         │
│  • Hadoop HDFS UI        → http://localhost:9870                         │
└──────────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### 1. Kafka Producer (`gpuz_producer.py`)
**Role**: Data ingestion and streaming
- Reads GPU-Z CSV log files
- Parses 32+ metrics per record
- Converts to structured JSON
- Publishes to Kafka topic
- Handles replay speed and looping

**Key Features**:
- Retry logic for Kafka connection
- Configurable replay speed (1x, 2x, etc.)
- Real-time simulation with time-based delays
- Error handling and logging

### 2. Apache Kafka
**Role**: Distributed message broker
- Decouples producers from consumers
- Provides durability and reliability
- Enables multiple consumers
- Handles backpressure

**Configuration**:
- Topic: `gpu-metrics`
- Partitions: 1 (can scale to multiple)
- Replication: 1 (single broker setup)

### 3. InfluxDB Consumer (`influxdb_consumer.py`)
**Role**: Real-time path - writes to time-series DB
- Consumes from Kafka topic
- Transforms data for InfluxDB
- Writes metrics with timestamps
- Enables real-time visualization

**Metrics Written**:
- Temperature metrics (GPU, CPU, memory)
- Clock speeds (GPU, memory)
- Load percentages
- Power consumption
- Memory usage
- Fan speeds
- Voltages

### 4. InfluxDB
**Role**: Time-series data storage
- Optimized for time-series data
- Flux query language
- Fast read/write performance
- Data retention policies

**Schema**:
- Measurement: `gpu_metrics`
- Fields: 15+ numeric metrics
- Timestamps: Nanosecond precision

### 5. Grafana
**Role**: Visualization and monitoring
- Real-time dashboards
- Custom panels and queries
- Alert rules
- Historical data exploration

**Features**:
- Time-series graphs
- Gauge panels
- Stat panels
- Alert notifications

### 6. Spark Streaming (`streaming_processor.py`)
**Role**: Real-time data processing
- Consumes from Kafka
- Window-based aggregations (30s windows)
- Anomaly detection
- Writes to HDFS for historical analysis

**Processing**:
- Avg, Max, Min aggregations
- Real-time alert generation
- Data enrichment
- Quality checks

### 7. Hadoop HDFS
**Role**: Distributed storage for historical data
- Stores processed metrics
- Parquet format (columnar, compressed)
- Enables batch analytics
- Scalable storage

**Structure**:
```
/gpu-metrics/          # Raw streaming data
/gpu-analytics/        # Processed analytics results
  ├── daily_statistics/
  ├── hourly_patterns/
  ├── temperature_spikes/
  └── correlations/
```

### 8. Batch Analytics (`batch_analytics.py`)
**Role**: Historical analysis and insights
- Reads from HDFS
- Computes daily/hourly statistics
- Detects patterns and anomalies
- Correlation analysis

**Outputs**:
- Daily summaries
- Hourly usage patterns
- Temperature spike events
- Metric correlations

## Data Flow Patterns

### Real-Time Flow (Milliseconds to Seconds)
```
GPU-Z Log → Kafka Producer → Kafka → InfluxDB Consumer → InfluxDB → Grafana
           (1-2s)          (<1s)    (<1s)               (<1s)      Real-time
```

### Batch Flow (Minutes to Hours)
```
Kafka → Spark Streaming → HDFS → Batch Analytics → Results
       (30s windows)     (append) (scheduled/manual) (HDFS)
```

## Scalability Considerations

### Horizontal Scaling
- **Kafka**: Add more partitions and brokers
- **Spark**: Add more worker nodes
- **HDFS**: Add more data nodes

### Vertical Scaling
- **Spark Workers**: Increase memory and cores
- **Kafka**: Increase heap size
- **InfluxDB**: Increase memory and disk I/O

### Performance Optimization
- Batch writes to InfluxDB
- Kafka compression (gzip)
- Parquet compression in HDFS
- Spark broadcast joins

## Fault Tolerance

### Data Durability
- **Kafka**: Message replication (configurable)
- **HDFS**: Block replication (default: 3)
- **InfluxDB**: Automatic backups (configurable)

### Failure Recovery
- **Kafka**: Auto-restart consumers from last offset
- **Spark**: Checkpointing for streaming jobs
- **Docker**: Container restart policies

## Monitoring & Observability

### Logs
- All components log to stdout/stderr
- Accessible via `docker-compose logs`
- Python logging with INFO level

### Metrics
- Spark UI: Job progress and performance
- Kafka: Topic lag and throughput
- InfluxDB: Database size and query performance
- Grafana: Dashboard usage and alerts

### Health Checks
- Docker container health status
- Kafka topic availability
- HDFS namenode status
- Web UI accessibility

## Security Considerations

### Current Setup (Development)
- No authentication on Kafka
- Basic auth on Grafana (admin/admin)
- Token auth on InfluxDB (configurable)
- Internal Docker network

### Production Recommendations
- Enable Kafka SASL/SSL
- Configure Grafana OAuth/LDAP
- Use InfluxDB API tokens with limited scope
- Implement HDFS ACLs
- Network segmentation
- TLS/SSL for all communications

## Performance Metrics

### Throughput
| Component | Throughput |
|-----------|-----------|
| Kafka Producer | 1-2 msg/s (log rate) |
| Kafka Broker | 1000+ msg/s |
| Spark Streaming | 100+ records/s |
| InfluxDB Writes | 60-120 points/min |

### Latency
| Path | Latency |
|------|---------|
| Producer → Kafka | < 100ms |
| Kafka → Consumer | < 50ms |
| Consumer → InfluxDB | < 200ms |
| InfluxDB → Grafana | < 500ms |
| **End-to-End** | **< 1 second** |

### Storage
| Component | Size (24h @ 1 rec/s) |
|-----------|---------------------|
| Kafka (retention) | ~86 MB |
| HDFS (Parquet) | ~30-50 MB |
| InfluxDB | ~50-70 MB |

## Technology Choices Rationale

### Why Kafka?
- Industry standard for streaming
- Decouples components
- Handles backpressure
- Supports multiple consumers

### Why Spark?
- Unified batch and streaming
- Rich API for transformations
- Integrates well with HDFS
- Scalable processing

### Why HDFS?
- Distributed storage
- Fault-tolerant
- Integrates with Spark
- Cost-effective for large data

### Why InfluxDB?
- Purpose-built for time-series
- Fast queries
- Good Grafana integration
- Built-in retention policies

### Why Grafana?
- Industry-standard visualization
- Rich plugin ecosystem
- Easy dashboard creation
- Built-in alerting

## Extension Points

### Add New Data Sources
- Modify Kafka producer to accept multiple inputs
- Create new topics for different GPUs/systems
- Merge streams in Spark

### Add New Analytics
- Extend batch analytics with new metrics
- Add ML models for predictions
- Implement custom aggregations

### Add New Visualizations
- Create custom Grafana panels
- Export data to other BI tools
- Build custom web dashboards

### Add Alerting
- Implement Grafana alerts
- Send notifications (email, Slack, etc.)
- Create alert escalation policies

---

**This architecture demonstrates production-grade data engineering patterns suitable for real-world streaming analytics applications.**
