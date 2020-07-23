from dnxdata.utils.utils import Utils
from dnxdata.utils.s3 import S3
from dnxdata.logger import Logger
import awswrangler as wr
import pandas as pd
import numpy as np


class Pandas:

    def __init__(self):
        self.utils = Utils()
        self.s3 = S3()
        self.logger = Logger("DNX Pandas =>")

    # You can pass list or string path or .parquet
    def get_parquet(self, path):

        self.logger.debug("Starting get_parquet")
        self.logger.debug("{}".format(path))

        keys_s3 = self.s3.get_list_parquet(path)
        self.logger.debug("S3keys {}".format(keys_s3))
        if len(keys_s3) == 0:
            self.logger.debug("Finishing get_parquet")
            return pd.DataFrame()

        df = wr.s3.read_parquet(
            path=keys_s3,
            dataset=True,
            validate_schema=False
        )

        self.logger.debug("Finishing get_parquet")

        return df

    def write_parquet(self, df, path, database, table, mode, partition_cols):

        self.logger.debug("Starting write_parquet")
        self.logger.debug("database.table {}.{}".format(database, table))
        self.logger.debug(
            "mode {} partition_cols {} path {}"
            .format(
                mode,
                partition_cols,
                path
            )
        )

        if df.empty:
            self.logger.debug("DataFrame is None")
        else:

            if partition_cols:
                wr.s3.to_parquet(
                    df=df,
                    path=path,
                    dataset=True,
                    database=database,
                    table=table,
                    mode=mode,
                    partition_cols=partition_cols,
                    compression='snappy'
                )
            else:
                wr.s3.to_parquet(
                    df=df,
                    path=path,
                    dataset=True,
                    database=database,
                    table=table,
                    mode=mode,
                    compression='snappy'
                )

        self.logger.debug("Finishing write_parquet")

    def print_dtypes(self, df):

        self.logger.debug("Starting print_dtypes")

        result = {}
        try:
            result = {k: str(v) for k, v in df.dtypes.items()}
        except Exception as e:
            self.logger.warning(e)
            pass

        index = {}
        try:
            index = {row for row in df.index.names}
        except Exception as e:
            self.logger.warning(e)
            pass

        self.logger.debug("List dtypes")
        self.logger.debug(result)
        self.logger.debug("List index")
        self.logger.debug(index)

        self.logger.debug("Finishing print_dtypes")

    def convert_dtypes(self, df, list_dtypes):

        self.logger.debug("Starting convert_dtypes")
        self.logger.debug("list_dtypes {}".format(list_dtypes))

        columns = []
        for col in df.dtypes.keys():
            columns.append(col)

        for column in columns:
            dtype = list_dtypes.get(column, None)

            if dtype is None:
                self.logger.warning(
                    "Column {} type {} doesn't in mapping, please verify."
                    .format(
                        column,
                        dtype
                    )
                )
                continue

            if dtype in ["int", "bigint"]:
                df[column] = pd.to_numeric(df[column], errors='coerce')
                df = df.replace(np.nan, 0, regex=True)
                df[column] = df[column].astype('float').astype('Int32')
            elif dtype == "datetime64":
                df[column] = pd.to_datetime(df[column])
            elif dtype == "str":
                df[column] = df[column].apply(str)
            elif dtype == "bool":
                df[column] = df[column].astype('bool')

        self.print_dtypes(df)
        self.logger.debug("Finishing convert_dtypes")

        return df

    def create_database_athena(self, database):

        if database not in wr.catalog.databases().values:
            wr.catalog.create_database(database)
            self.logger.debug(
                "Database {} created in Data Lake"
                .format(
                    database
                )
            )

    def delete_table_athena(self, database, table):

        self.logger.debug("Starting delete_table_athena")
        self.logger.debug("database {} table {}".format(database, table))

        wr.catalog.delete_table_if_exists(
            database=database,
            table=table
        )

        self.logger.debug("Finishing delete_table_athena")
