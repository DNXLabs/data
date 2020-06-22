from src.lib.utils.utils import Utils
from src.lib.utils.boto3 import Boto3
from src.lib.logger import info, debug, error
import awswrangler as wr
import pandas as pd


class Pandas:

    def __init__(self, region=None):
        self.region = region
        self.utils = Utils()
        self.s3 = Boto3()

    # You can pass list or string path or .parquet
    def get_parquet(self, path):
        info("Starting GetParquet {}".format(path))

        keys_s3 = self.s3.get_list_parquet(path)
        info("S3keys {}".format(keys_s3))
        if len(keys_s3) == 0:
            return pd.DataFrame()
            info("Finishing GetParquet")

        df = wr.s3.read_parquet(
            path=keys_s3,
            dataset=True,
            validate_schema=False
        )

        info("Finishing GetParquet")

        return df

    def write_parquet(self, df, path, database, table, mode, partition_cols, list_path_delete):
        info("Starting Write Parquet")

        if (list_path_delete is not None) & (mode != "append"):
            info(
                "list_path_delete => {}"
                .format(list_path_delete)
            )
            self.s3.delete_file_s3(
                path=list_path_delete,
                path_or_key="key",
                verbose=False
            )

        if df.empty:
            info("DF Write Parquet None or only lines with delete")
        else:
            df["dt_process_parq"] = self.utils.date_time()
            df["dt_process_parq"] = pd.to_datetime(df["dt_process_parq"])

            if partition_cols:
                wr.s3.to_parquet(
                    df=df, path=path, dataset=True, database=database, table=table,
                    mode=mode, partition_cols=partition_cols, compression='snappy'
                )
            else:
                wr.s3.to_parquet(
                    df=df, path=path, dataset=True, database=database,
                    table=table, mode=mode, compression='snappy'
                )

        info("Finishing Write Parquet")

    def print_dtypes(self, df):
        debug("Starting print_dtypes")

        result = {}
        try:
            result = {k: str(v) for k, v in df.dtypes.items()}
        except Exception as e:
            error(e)
            pass

        index = {}
        try:
            index = {row for row in df.index.names}
        except Exception as e:
            error(e)
            pass

        debug("List dtypes")
        debug(result)
        debug("List index")
        debug(index)

        debug("Finishing GetDtypesDf")
