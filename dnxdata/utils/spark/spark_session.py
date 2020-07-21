import sys
from pyspark import SparkFiles
from pyspark.sql import SparkSession
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from dnxdata.logger import Logger


logger = Logger("Metrics-Transformer =>")


def _spark():

    logger.debug("Starting SparkSession")

    spark = SparkSession \
        .builder.appName("Metrics-Transformer => - Data ETL Glue") \
        .config("hive.exec.dynamic.partition", "true") \
        .config("hive.exec.dynamic.partition.mode", "nonstrict") \
        .enableHiveSupport() \
        .getOrCreate()

    sys.path.insert(0, SparkFiles.getRootDirectory())

    logger.debug("Finishing SparkSession")

    return spark


def _glue_context():

    logger.debug("Starting glue_context")

    glue = GlueContext(SparkContext.getOrCreate())

    logger.debug("Finishing glue_context")

    return glue


spark = _spark()

glue_context = _glue_context()
