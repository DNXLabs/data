import sys
from pyspark import SparkFiles
from pyspark.sql import SparkSession
from pyspark.context import SparkContext
from awsglue.context import GlueContext


class ModSparkSession:

    def __init__(self):
        pass

    def start(self):
        self.spark = SparkSession.builder \
                                 .appName("Metrics-Common - Data ETL Glue") \
                                 .enableHiveSupport() \
                                 .getOrCreate()
        sys.path.insert(0, SparkFiles.getRootDirectory())

        self.log4jLogger = self.spark._jvm.org.apache.log4j
        self.glue_context = GlueContext(SparkContext.getOrCreate())
        self.spark.conf.set(
            "spark.sql.legacy.allowCreatingManagedTableUsingNonemptyLocation",
            "true"
        )
        return [self.spark, self.log4jLogger, self.glue_context]
