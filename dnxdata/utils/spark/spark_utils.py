import sys
from pyspark.sql.functions import (when, col, trim, lit)
from dnxdata.utils.utils import Utils
from dnxdata.utils.s3 import S3
from dnxdata.logger import Logger


class SparkUtils:

    def __init__(self, spark, glue_context):
        self.logger = Logger("Metrics-Utils =>")
        self.spark = spark
        self.glue_context = glue_context
        self.utils = Utils()
        self.s3 = S3()

    def write_parquet(self, df, path, partition_column, mode, database, table):

        self.logger.info("Starting write_parquet")
        dbtable = "{}.{}".format(database, table)
        self.logger.info("database.table => {}".format(dbtable))

        self.is_empty_df(df=df, exit_none=True)

        self.spark.catalog.setCurrentDatabase(database)

        if len(partition_column) > 0:

            df.write. \
                format("parquet"). \
                partitionBy(partition_column). \
                saveAsTable(
                        dbtable,
                        mode=mode,
                        path=path
                )
        else:

            df.write. \
                format("parquet"). \
                saveAsTable(
                        dbtable,
                        mode=mode,
                        path=path
                )

        self.spark.catalog.refreshTable("{}.{}".format(database, table))

        self.logger.info("Finishing write_parquet")

    def is_empty_df(self, df, exit_none=False):

        self.logger.debug("Starting is_empty_df")
        self.logger.debug("exit_none {}".format(exit_none))

        v_invalid_df = True if df.rdd.isEmpty() else False

        if exit_none & v_invalid_df:
            self.logger.info("Invalid DF {}".format(v_invalid_df))
            sys.exit(1)
            return

        self.logger.debug("v_invalid_df {}".format(v_invalid_df))

        self.logger.debug("Finishing is_empty_df")

        return v_invalid_df

    def union_df(self, df1, df2):

        self.logger.info("Starting union_df")
        self.logger.debug("count df1 {}".format(df1.count()))
        self.logger.debug("count df2 {}".format(df2.count()))

        # Add missing columns to df1
        df_left = df1
        for column in set(df2.columns) - set(df1.columns):
            df_left = df_left.withColumn(column, lit(None))

        # Add missing columns to df2
        df_right = df2
        for column in set(df1.columns) - set(df2.columns):
            df_right = df_right.withColumn(column, lit(None))

        # Make sure columns are ordered the same
        df = df_left.union(df_right.select(df_left.columns))

        self.logger.debug("count union {}".format(df.count()))

        self.logger.info("Finishing union_df")

        return df

    def convert_dtypes(self, df, list_dtypes):

        self.logger.info("Starting convert_dtypes")
        self.logger.info("list_col_dtypes {}".format(list_dtypes))

        dtypes = df.dtypes
        for row in dtypes:
            column = row[0]
            dtype = list_dtypes.get(column)

            if dtype is None:
                self.logger.warning(
                    "Column {} type {} doesn't in mapping, please verify."
                    .format(
                        column,
                        dtype
                    )
                )
                continue

            equal_number = dtype in ["double", "integer", "float"]
            find_decimal = dtype.find("decimal") >= 0
            if equal_number or find_decimal:
                df = df.withColumn(
                    column,
                    when(trim(col(column)).isNull(), "0")
                    .otherwise(trim(col(column)))
                )
                df = df.withColumn(column, col(column).cast(dtype))

            elif dtype == "string":
                df = df.withColumn(column, trim(col(column)))

            elif dtype == "timestamp":
                df = df.withColumn(column, trim(col(column)).cast(dtype))

        self.logger.info("Finishing convert_dtypes")

        return df

    def get_data_rds(self, connection_type, connection_settings):

        self.logger.info("Starting get_data_rds")

        if connection_type == "mysql":
            conn = {
                "url": "jdbc:mysql://{}:{}/{}".format(
                    connection_settings.get("host"),
                    connection_settings.get("port"),
                    connection_settings.get("schema")
                ),
                "dbtable": connection_settings.get("dbtable"),
                "user": connection_settings.get("user"),
                "password": connection_settings.get("passwd")
            }

            df = self.glue_context.create_dynamic_frame.from_options(
                connection_type=connection_type,
                connection_options=conn
            )

            df = df.toDF()

        self.logger.info("Start Show DF RDS")
        df.printSchema()
        df.show()
        self.logger.info("Finish Show DF RDS")

        self.logger.info("Finishing get_data_rds")

        return df
