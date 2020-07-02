from dnxdata.utils.utils import Utils
from dnxdata.utils.s3 import S3
from dnxdata.logger import Logger
import awswrangler as wr
import pandas as pd
import numpy as np


class Pandas:

    def __init__(self, region=None):
        self.region = region
        self.utils = Utils()
        self.s3 = S3()
        self.logger = Logger("DNX Pandas =>")

    # You can pass list or string path or .parquet
    def get_parquet(self, path):

        self.logger.debug("Starting get_parquet {}".format(path))

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

    def write_parquet(self, df, path, database, table, mode, partition_cols, list_path_delete):

        self.logger.debug("Starting Write Parquet")

        if (list_path_delete is not None) & (mode != "append"):
            self.logger.debug(
                "list_path_delete => {}"
                .format(list_path_delete)
            )
            self.s3.delete_file_s3(
                path=list_path_delete,
                path_or_key="key"
            )

        if df.empty:
            self.logger.debug(
                "DF is None or DF have to only lines with delete"
            )
        else:
            df["dt_process_parq"] = self.utils.date_time()
            df["dt_process_parq"] = pd.to_datetime(df["dt_process_parq"])

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

        self.logger.debug("Finishing Write Parquet")

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

        self.logger.debug("Starting fix_dtypes")

        columns = []
        for col in df.dtypes.keys():
            columns.append(col)

        for column in columns:
            dtype = list_dtypes.get(column)

            if dtype is None:
                self.logger.warning(
                    "Column {} type {} doesn't in mapping, please verify."
                    .format(
                        column,
                        dtype
                    )
                )

            if dtype in ["int", "bigint"]:
                df[column] = pd.to_numeric(df[column], errors='coerce')
                df = df.replace(np.nan, 0, regex=True)
                df[column] = df[column].astype('float').astype('int')
            elif dtype == "datetime64":
                df[column] = pd.to_datetime(df[column])
            elif dtype == "str":
                df[column] = df[column].apply(str)
            elif dtype == "bool":
                df[column] = df[column].astype('bool')

        self.print_dtypes(df)
        self.logger.debug("Finishing fix_dtypes")

        return df
