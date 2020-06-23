import sys
from pyspark.sql.functions import lit
from pyspark.sql.functions import (when, col, trim)
from pyspark.sql import functions as F
from dnxdata.utils.utils import Utils
from dnxdata.utils.boto3 import Boto3


class SparkUtils:

    def __init__(self, spark, glue_context, log4jLogger):
        self.spark = spark
        self.log4jLogger = log4jLogger
        self.glue_context = glue_context
        self.utils = Utils()
        self.s3 = Boto3()

    def save_table(self, df, path, partition_column, mode, database, table, list_path_delete):
        # TODO Why using another log manager?
        logger = self.log4jLogger.LogManager.getLogger(__name__ + "." + self.__class__.__name__ + "." + sys._getframe().f_code.co_name)

        logger.info("Metrics-Common => Starting save table")
        logger.info(
            "Metrics-Common => Database + Table {}.{}"
            .format(
                database,
                table
            )
        )

        self.is_empty_df(df=df, exit_none=True)

        self.spark.catalog.setCurrentDatabase(database)

        df = df.withColumn("dt_process_parq", lit(self.utils.date_time()).cast("timestamp"))

        if len(list_path_delete) > 0:
            self.s3.delete_file_s3(path=list_path_delete, path_or_key="path")

        write_obj = df.write. \
            format("parquet"). \
            option("path", path). \
            option("mergeSchema", "true"). \
            option("compression", "snappy"). \
            mode(mode.replace("merge", "append"))

        if len(partition_column) > 0:
            write_obj = write_obj.partitionBy(partition_column)

        write_obj.saveAsTable(table)

        self.spark.catalog.refreshTable("{}.{}".format(database, table))

        logger.info("Metrics-Common => Finishing save table")

    def is_empty_df(self, df, exit_none=False):
        # TODO Why using another log manager?
        logger = self.log4jLogger.LogManager.getLogger(
            __name__ + "." + self.__class__.__name__ + "." + sys._getframe().f_code.co_name
        )

        logger.info("Metrics-Common => Starting IsEmptyDf")

        v_invalid_df = True if df.rdd.isEmpty() else False

        if exit_none & v_invalid_df:
            logger.info("Metrics-Common => IsEmptyDf Invalid Data Frame v_invalid_df {}".format(v_invalid_df))
            sys.exit(1)
            return

        logger.info(
            "Metrics-Common => Finishing IsEmptyDf v_invalid_df {}"
            .format(v_invalid_df)
        )

        return v_invalid_df

    def union_data_frame(self, df1, df2):
        # TODO Why using another log manager?
        logger = self.log4jLogger.LogManager.getLogger(__name__ + "." + self.__class__.__name__ + "." + sys._getframe().f_code.co_name)

        logger.info("Metrics-Common => Starting UnionDataFrame")
        logger.info("Metrics-Common => count 1 {}".format(df1.count()))
        logger.info("Metrics-Common => count 2 {}".format(df2.count()))

        # Add missing columns to df1
        df_left = df1
        for column in set(df2.columns) - set(df1.columns):
            df_left = df_left.withColumn(column, F.lit(None))

        # Add missing columns to df2
        df_right = df2
        for column in set(df1.columns) - set(df2.columns):
            df_right = df_right.withColumn(column, F.lit(None))

        logger.info("Metrics-Common => Finishing UnionDataFrame")

        # Make sure columns are ordered the same
        df = df_left.union(df_right.select(df_left.columns))
        logger.info("Metrics-Common => count 3 {}".format(df.count()))
        return df

    def fix_dtypes(self, df, list_col_dtypes, col_name_last_update):
        logger = self.log4jLogger.LogManager.getLogger(__name__ + "." + self.__class__.__name__ + "." + sys._getframe().f_code.co_name)

        logger.info("Metrics-Common => Starting FixValueNull")
        logger.info("Metrics-Common => list_col_dtypes {}".format(list_col_dtypes))

        dtypes = df.dtypes
        for row in dtypes:
            column = row[0]
            _dtypes = list_col_dtypes.get(column)

            if _dtypes is None:
                logger.info("Metrics-Common => Column not parameterized {}".format(row))
                continue

            if (_dtypes in ["double", "integer", "float"]) | (_dtypes.find("decimal") >= 0):
                logger.info("Metrics-Common => FixValueNull Number row {}".format(row))
                df = df.withColumn(column, when(trim(col(column)).isNull(), "0")
                                   .otherwise(trim(col(column))))
                df = df.withColumn(column, col(column).cast(_dtypes))
            elif _dtypes == "string":
                logger.info("Metrics-Common => FixValueNull String row {}".format(row))
                df = df.withColumn(column, trim(col(column)))

            elif _dtypes == "timestamp":
                logger.info("Metrics-Common => FixValueNull Timestamp row {}".format(row))
                if column == col_name_last_update:
                    df = df.withColumn(column, trim(col(column)).cast(_dtypes))
                else:
                    df = df.withColumn(column, trim(col(column)).cast("string"))

        logger.info("Metrics-Common => Finishing FixValueNull")
        return df

    def get_data_rds(self, connection_type, connection_settings):

        logger = self.log4jLogger.LogManager.getLogger(__name__ + "." + self.__class__.__name__ + "." + sys._getframe().f_code.co_name)
        logger.info("Metrics-Common => Starting get_data_rds")

        if connection_type == "mysql":
            conn = {
                "url": "jdbc:mysql://{}:{}/{}".format(
                    connection_settings.get("host"),
                    connection_settings.get("port"),
                    connection_settings.get("schema")
                ),
                "dbtable": connection_settings.get("dbtable"),
                "user": connection_settings.get("user"),
                "password": connection_settings.get("passwd")}

            df = self.glue_context.create_dynamic_frame.from_options(
                connection_type=connection_type,
                connection_options=conn
            )

            df = df.toDF()

        logger.info("Metrics-Common => Start Show Data frame RDS")
        df.printSchema()
        df.show()
        logger.info("Metrics-Common => Finish Show Data frame RDS")

        logger.info("Metrics-Common => Finishing get_data_rds")

        return df
