"""
Spark Streaming Job for GPU Metrics Processing
Real-time processing of GPU metrics from Kafka
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GPUMetricsProcessor:
    def __init__(self, app_name="GPUMetricsStreaming"):
        """Initialize Spark Session"""
        self.spark = SparkSession.builder \
            .appName(app_name) \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
            .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint") \
            .getOrCreate()

        self.spark.sparkContext.setLogLevel("WARN")
        logger.info("Spark session created successfully")

    def define_schema(self):
        """Define schema for GPU metrics"""
        return StructType([
            StructField("Date", StringType(), True),
            StructField("timestamp", StringType(), True),
            StructField("GPU Clock", DoubleType(), True),
            StructField("Memory Clock", DoubleType(), True),
            StructField("GPU Temperature", DoubleType(), True),
            StructField("Hot Spot", DoubleType(), True),
            StructField("Memory Temperature", DoubleType(), True),
            StructField("Fan 1 Speed (%)", DoubleType(), True),
            StructField("Fan 1 Speed (RPM)", DoubleType(), True),
            StructField("Fan 2 Speed (%)", DoubleType(), True),
            StructField("Fan 2 Speed (RPM)", DoubleType(), True),
            StructField("Memory Used", DoubleType(), True),
            StructField("GPU Load", DoubleType(), True),
            StructField("Memory Controller Load", DoubleType(), True),
            StructField("Video Engine Load", DoubleType(), True),
            StructField("Bus Interface Load", DoubleType(), True),
            StructField("Board Power Draw", DoubleType(), True),
            StructField("GPU Chip Power Draw", DoubleType(), True),
            StructField("MVDDC Power Draw", DoubleType(), True),
            StructField("PWR_SRC Power Draw", DoubleType(), True),
            StructField("PWR_SRC Voltage", DoubleType(), True),
            StructField("PCIe Slot Power", DoubleType(), True),
            StructField("PCIe Slot Voltage", DoubleType(), True),
            StructField("8-Pin #1 Power", DoubleType(), True),
            StructField("8-Pin #1 Voltage", DoubleType(), True),
            StructField("8-Pin #2 Power", DoubleType(), True),
            StructField("8-Pin #2 Voltage", DoubleType(), True),
            StructField("8-Pin #3 Power", DoubleType(), True),
            StructField("8-Pin #3 Voltage", DoubleType(), True),
            StructField("Power Consumption (%)", DoubleType(), True),
            StructField("PerfCap Reason", DoubleType(), True),
            StructField("GPU Voltage", DoubleType(), True),
            StructField("CPU Temperature", DoubleType(), True),
            StructField("System Memory Used", DoubleType(), True)
        ])

    def read_from_kafka(self, kafka_broker="kafka:9093", topic="gpu-metrics"):
        """Read streaming data from Kafka"""
        logger.info(f"Reading from Kafka topic: {topic}")

        df = self.spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", kafka_broker) \
            .option("subscribe", topic) \
            .option("startingOffsets", "latest") \
            .load()

        # Parse JSON data
        schema = self.define_schema()

        parsed_df = df.select(
            from_json(col("value").cast("string"), schema).alias("data"),
            col("timestamp").alias("kafka_timestamp")
        ).select("data.*", "kafka_timestamp")

        return parsed_df

    def compute_aggregations(self, df, window_duration="30 seconds"):
        """Compute real-time aggregations"""
        logger.info(f"Computing aggregations with window: {window_duration}")

        # Convert timestamp string to timestamp type
        df_with_ts = df.withColumn(
            "event_time",
            to_timestamp(col("timestamp"))
        )

        # Compute windowed aggregations
        aggregated = df_with_ts \
            .withWatermark("event_time", "1 minute") \
            .groupBy(
                window(col("event_time"), window_duration)
            ) \
            .agg(
                # GPU metrics
                avg("GPU Temperature").alias("avg_gpu_temp"),
                max("GPU Temperature").alias("max_gpu_temp"),
                min("GPU Temperature").alias("min_gpu_temp"),

                avg("Hot Spot").alias("avg_hot_spot"),
                max("Hot Spot").alias("max_hot_spot"),

                # CPU metrics
                avg("CPU Temperature").alias("avg_cpu_temp"),
                max("CPU Temperature").alias("max_cpu_temp"),

                # Load metrics
                avg("GPU Load").alias("avg_gpu_load"),
                max("GPU Load").alias("max_gpu_load"),

                # Power metrics
                avg("Board Power Draw").alias("avg_power_draw"),
                max("Board Power Draw").alias("max_power_draw"),
                min("Board Power Draw").alias("min_power_draw"),

                # Memory metrics
                avg("Memory Used").alias("avg_memory_used"),
                max("Memory Used").alias("max_memory_used"),

                avg("System Memory Used").alias("avg_system_memory"),
                max("System Memory Used").alias("max_system_memory"),

                # Clock metrics
                avg("GPU Clock").alias("avg_gpu_clock"),
                avg("Memory Clock").alias("avg_memory_clock"),

                # Count
                count("*").alias("record_count")
            )

        return aggregated

    def detect_anomalies(self, df):
        """Detect anomalies in GPU metrics"""
        logger.info("Adding anomaly detection")

        # Define thresholds
        anomaly_df = df.withColumn(
            "high_temp_alert",
            when(col("GPU Temperature") > 85, True).otherwise(False)
        ).withColumn(
            "high_cpu_temp_alert",
            when(col("CPU Temperature") > 80, True).otherwise(False)
        ).withColumn(
            "high_power_alert",
            when(col("Board Power Draw") > 300, True).otherwise(False)
        ).withColumn(
            "high_load_alert",
            when(col("GPU Load") > 95, True).otherwise(False)
        )

        return anomaly_df

    def write_to_hdfs(self, df, output_path="/gpu-metrics"):
        """Write processed data to HDFS"""
        logger.info(f"Writing to HDFS: {output_path}")

        query = df.writeStream \
            .format("parquet") \
            .option("path", f"hdfs://namenode:9000{output_path}") \
            .option("checkpointLocation", f"/tmp/checkpoint/hdfs") \
            .outputMode("append") \
            .start()

        return query

    def write_to_console(self, df, truncate=False):
        """Write to console for debugging"""
        logger.info("Writing to console")

        query = df.writeStream \
            .format("console") \
            .option("truncate", truncate) \
            .outputMode("update") \
            .start()

        return query

    def process_streaming_metrics(self, kafka_broker="kafka:9093", topic="gpu-metrics"):
        """Main processing pipeline"""
        logger.info("Starting streaming metrics processing")

        # Read from Kafka
        raw_df = self.read_from_kafka(kafka_broker, topic)

        # Add anomaly detection
        anomaly_df = self.detect_anomalies(raw_df)

        # Compute aggregations
        aggregated_df = self.compute_aggregations(anomaly_df)

        # Write raw data to HDFS (for historical analysis)
        hdfs_query = self.write_to_hdfs(
            anomaly_df.select(
                "timestamp",
                "GPU Temperature",
                "CPU Temperature",
                "GPU Load",
                "Board Power Draw",
                "Memory Used",
                "System Memory Used",
                "GPU Clock",
                "Memory Clock",
                "high_temp_alert",
                "high_cpu_temp_alert",
                "high_power_alert",
                "high_load_alert"
            )
        )

        # Write aggregations to console (in production, write to another Kafka topic or database)
        console_query = self.write_to_console(aggregated_df)

        # Keep streaming running
        logger.info("Streaming queries started. Waiting for termination...")
        self.spark.streams.awaitAnyTermination()

    def stop(self):
        """Stop Spark session"""
        self.spark.stop()
        logger.info("Spark session stopped")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Process GPU metrics from Kafka')
    parser.add_argument('--broker', default='kafka:9093', help='Kafka broker address')
    parser.add_argument('--topic', default='gpu-metrics', help='Kafka topic name')

    args = parser.parse_args()

    processor = GPUMetricsProcessor()

    try:
        processor.process_streaming_metrics(
            kafka_broker=args.broker,
            topic=args.topic
        )
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    finally:
        processor.stop()


if __name__ == '__main__':
    main()
