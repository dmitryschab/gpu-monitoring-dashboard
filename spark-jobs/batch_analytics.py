"""
Batch Analytics Job for Historical GPU Metrics
Analyzes historical data stored in HDFS
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.window import Window
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GPUBatchAnalytics:
    def __init__(self, app_name="GPUBatchAnalytics"):
        """Initialize Spark Session for batch processing"""
        self.spark = SparkSession.builder \
            .appName(app_name) \
            .config("spark.sql.adaptive.enabled", "true") \
            .getOrCreate()

        self.spark.sparkContext.setLogLevel("WARN")
        logger.info("Spark session created for batch analytics")

    def read_from_hdfs(self, input_path="/gpu-metrics"):
        """Read historical data from HDFS"""
        logger.info(f"Reading data from HDFS: {input_path}")

        df = self.spark.read \
            .format("parquet") \
            .load(f"hdfs://namenode:9000{input_path}")

        logger.info(f"Loaded {df.count()} records from HDFS")
        return df

    def compute_daily_statistics(self, df):
        """Compute daily statistics for GPU metrics"""
        logger.info("Computing daily statistics...")

        # Convert timestamp to date
        df_with_date = df.withColumn(
            "date",
            to_date(col("timestamp"))
        )

        # Compute daily aggregations
        daily_stats = df_with_date.groupBy("date").agg(
            # Temperature stats
            avg("GPU Temperature").alias("avg_gpu_temp"),
            max("GPU Temperature").alias("max_gpu_temp"),
            min("GPU Temperature").alias("min_gpu_temp"),
            stddev("GPU Temperature").alias("stddev_gpu_temp"),

            avg("CPU Temperature").alias("avg_cpu_temp"),
            max("CPU Temperature").alias("max_cpu_temp"),
            min("CPU Temperature").alias("min_cpu_temp"),

            # Load stats
            avg("GPU Load").alias("avg_gpu_load"),
            max("GPU Load").alias("max_gpu_load"),
            percentile_approx("GPU Load", 0.95).alias("p95_gpu_load"),

            # Power stats
            avg("Board Power Draw").alias("avg_power_draw"),
            max("Board Power Draw").alias("max_power_draw"),
            min("Board Power Draw").alias("min_power_draw"),
            sum("Board Power Draw").alias("total_power_consumption"),

            # Memory stats
            avg("Memory Used").alias("avg_gpu_memory"),
            max("Memory Used").alias("max_gpu_memory"),
            avg("System Memory Used").alias("avg_system_memory"),
            max("System Memory Used").alias("max_system_memory"),

            # Alert counts
            sum(when(col("high_temp_alert") == True, 1).otherwise(0)).alias("high_temp_alert_count"),
            sum(when(col("high_cpu_temp_alert") == True, 1).otherwise(0)).alias("high_cpu_temp_alert_count"),
            sum(when(col("high_power_alert") == True, 1).otherwise(0)).alias("high_power_alert_count"),
            sum(when(col("high_load_alert") == True, 1).otherwise(0)).alias("high_load_alert_count"),

            # Record count
            count("*").alias("record_count")
        ).orderBy("date")

        return daily_stats

    def compute_hourly_patterns(self, df):
        """Analyze hourly usage patterns"""
        logger.info("Computing hourly patterns...")

        # Extract hour from timestamp
        df_with_hour = df.withColumn(
            "hour",
            hour(col("timestamp"))
        )

        # Compute hourly aggregations
        hourly_patterns = df_with_hour.groupBy("hour").agg(
            avg("GPU Temperature").alias("avg_gpu_temp"),
            avg("CPU Temperature").alias("avg_cpu_temp"),
            avg("GPU Load").alias("avg_gpu_load"),
            avg("Board Power Draw").alias("avg_power_draw"),
            count("*").alias("record_count")
        ).orderBy("hour")

        return hourly_patterns

    def detect_temperature_spikes(self, df, threshold=10.0):
        """Detect sudden temperature spikes"""
        logger.info(f"Detecting temperature spikes (threshold: {threshold}°C)...")

        # Create window for looking at previous values
        window_spec = Window.orderBy("timestamp")

        # Calculate temperature change
        df_with_change = df.withColumn(
            "prev_gpu_temp",
            lag("GPU Temperature", 1).over(window_spec)
        ).withColumn(
            "gpu_temp_change",
            col("GPU Temperature") - col("prev_gpu_temp")
        ).withColumn(
            "prev_cpu_temp",
            lag("CPU Temperature", 1).over(window_spec)
        ).withColumn(
            "cpu_temp_change",
            col("CPU Temperature") - col("prev_cpu_temp")
        )

        # Filter for spikes
        spikes = df_with_change.filter(
            (col("gpu_temp_change") > threshold) |
            (col("cpu_temp_change") > threshold)
        ).select(
            "timestamp",
            "GPU Temperature",
            "prev_gpu_temp",
            "gpu_temp_change",
            "CPU Temperature",
            "prev_cpu_temp",
            "cpu_temp_change",
            "GPU Load",
            "Board Power Draw"
        ).orderBy("timestamp")

        return spikes

    def compute_correlation_analysis(self, df):
        """Compute correlations between different metrics"""
        logger.info("Computing correlation analysis...")

        # Select numeric columns for correlation
        metrics = [
            "GPU Temperature",
            "CPU Temperature",
            "GPU Load",
            "Board Power Draw",
            "Memory Used",
            "GPU Clock"
        ]

        # Compute correlation matrix
        correlations = []
        for metric1 in metrics:
            for metric2 in metrics:
                if metric1 != metric2:
                    corr = df.stat.corr(metric1, metric2)
                    correlations.append({
                        "metric1": metric1,
                        "metric2": metric2,
                        "correlation": round(corr, 4)
                    })

        # Convert to DataFrame
        corr_df = self.spark.createDataFrame(correlations)
        corr_df = corr_df.orderBy(abs(col("correlation")).desc())

        return corr_df

    def generate_summary_report(self, df):
        """Generate overall summary report"""
        logger.info("Generating summary report...")

        summary = df.select(
            # Temperature summary
            avg("GPU Temperature").alias("avg_gpu_temp"),
            max("GPU Temperature").alias("max_gpu_temp"),
            min("GPU Temperature").alias("min_gpu_temp"),

            avg("CPU Temperature").alias("avg_cpu_temp"),
            max("CPU Temperature").alias("max_cpu_temp"),
            min("CPU Temperature").alias("min_cpu_temp"),

            # Load summary
            avg("GPU Load").alias("avg_gpu_load"),
            max("GPU Load").alias("max_gpu_load"),

            # Power summary
            avg("Board Power Draw").alias("avg_power_draw"),
            max("Board Power Draw").alias("max_power_draw"),
            sum("Board Power Draw").alias("total_power_consumption"),

            # Clock summary
            avg("GPU Clock").alias("avg_gpu_clock"),
            avg("Memory Clock").alias("avg_memory_clock"),

            # Memory summary
            avg("Memory Used").alias("avg_gpu_memory"),
            max("Memory Used").alias("max_gpu_memory"),

            # Total records
            count("*").alias("total_records")
        )

        return summary

    def run_analytics(self, input_path="/gpu-metrics", output_path="/gpu-analytics"):
        """Run all analytics jobs"""
        logger.info("Starting batch analytics...")

        # Read data
        df = self.read_from_hdfs(input_path)

        # Generate various analytics
        logger.info("=" * 60)
        logger.info("SUMMARY REPORT")
        logger.info("=" * 60)
        summary = self.generate_summary_report(df)
        summary.show(truncate=False)

        logger.info("=" * 60)
        logger.info("DAILY STATISTICS")
        logger.info("=" * 60)
        daily_stats = self.compute_daily_statistics(df)
        daily_stats.show(truncate=False)

        logger.info("=" * 60)
        logger.info("HOURLY PATTERNS")
        logger.info("=" * 60)
        hourly_patterns = self.compute_hourly_patterns(df)
        hourly_patterns.show(24, truncate=False)

        logger.info("=" * 60)
        logger.info("TEMPERATURE SPIKES")
        logger.info("=" * 60)
        spikes = self.detect_temperature_spikes(df, threshold=5.0)
        spikes.show(20, truncate=False)

        logger.info("=" * 60)
        logger.info("CORRELATION ANALYSIS")
        logger.info("=" * 60)
        correlations = self.compute_correlation_analysis(df)
        correlations.show(20, truncate=False)

        # Save results to HDFS
        logger.info(f"Saving results to HDFS: {output_path}")

        daily_stats.write.mode("overwrite").parquet(
            f"hdfs://namenode:9000{output_path}/daily_statistics"
        )

        hourly_patterns.write.mode("overwrite").parquet(
            f"hdfs://namenode:9000{output_path}/hourly_patterns"
        )

        spikes.write.mode("overwrite").parquet(
            f"hdfs://namenode:9000{output_path}/temperature_spikes"
        )

        correlations.write.mode("overwrite").parquet(
            f"hdfs://namenode:9000{output_path}/correlations"
        )

        logger.info("Analytics complete!")

    def stop(self):
        """Stop Spark session"""
        self.spark.stop()
        logger.info("Spark session stopped")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Run batch analytics on GPU metrics')
    parser.add_argument('--input', default='/gpu-metrics', help='HDFS input path')
    parser.add_argument('--output', default='/gpu-analytics', help='HDFS output path')

    args = parser.parse_args()

    analytics = GPUBatchAnalytics()

    try:
        analytics.run_analytics(
            input_path=args.input,
            output_path=args.output
        )
    except Exception as e:
        logger.error(f"Error running analytics: {e}")
        raise
    finally:
        analytics.stop()


if __name__ == '__main__':
    main()
