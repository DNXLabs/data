from dnxdata.utils.utils import Utils
from dnxdata.utils.boto3 import Boto3
from dnxdata.logger import Logger
import awswrangler as wr
import pandas as pd


class Pandas:

    def __init__(self, region=None):
        self.region = region
        self.utils = Utils()
        self.s3 = Boto3()
        self.logger = Logger("DNX Pandas =>")

    # You can pass list or string path or .parquet
    def get_parquet(self, path):
        self.logger.info("Starting GetParquet {}".format(path))

        keys_s3 = self.s3.get_list_parquet(path)
        self.logger.info("S3keys {}".format(keys_s3))
        if len(keys_s3) == 0:
            self.logger.info("Finishing GetParquet")
            return pd.DataFrame()

        df = wr.s3.read_parquet(
            path=keys_s3,
            dataset=True,
            validate_schema=False
        )

        self.logger.info("Finishing GetParquet")

        return df

    def write_parquet(self, df, path, database, table, mode, partition_cols, list_path_delete):
        self.logger.info("Starting Write Parquet")

        if (list_path_delete is not None) & (mode != "append"):
            self.logger.info(
                "list_path_delete => {}"
                .format(list_path_delete)
            )
            self.s3.delete_file_s3(
                path=list_path_delete,
                path_or_key="key"
            )

        if df.empty:
            self.logger.info("DF Write Parquet None or only lines with delete")
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

        self.logger.info("Finishing Write Parquet")

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

        self.logger.debug("Finishing GetDtypesDf")
