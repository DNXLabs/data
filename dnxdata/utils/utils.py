import dateutil.tz
from datetime import datetime, timedelta
import time
from dnxdata.logger import Logger
from dnxdata.utils.constants import TIMESTAMP


class Utils:

    def __init__(self):
        self.logger = Logger("DNX Utils =>")

    def get_bucket_key(self, path):
        """
        Ex:
        path: 's3://bucket/folder0/folder1/key.csv'
        return
        bucket: 'bucket'
        key: 'folder0/folder1'
        """

        path = path.strip().replace("s3://", "")
        bucket = path.strip().split("/")[0]
        key = "/".join(path.split("/")[1:-1])

        source = {"bucket": bucket.strip(), "key": key.strip()}

        return source

    def get_path_file_processed(self, path, file_status):
        """
        Ex:
        path: 's3://bucket/folder0/folder1/key.csv'
        status: SUCCEEDED
        return
        key_dest: 'SUCCEED_20200522_164047_file.gz'
        """
        path = path.replace("s3://", "")
        key = "".join((("/".join(path.split("/")[1:])).split("/")[-1:]))

        time_format = "%Y%m%d_%H%M%S"
        key_dest = "{}_{}_.".format(
                        file_status,
                        self.date_time(format_date=False).strftime(time_format)
                    )
        key_dest = key_dest.replace(".", key)

        return key_dest

    def date_time(self, format_date=True,
                  timezone="Australia/Sydney", milliseconds=False):
        eastern = dateutil.tz.gettz(timezone)
        dt = datetime.now(tz=eastern)

        if format_date:
            if milliseconds:
                dt = dt.strftime("%Y-%m-%d %H:%M:%S:%f")
            else:
                dt = dt.strftime("%Y-%m-%d %H:%M:%S")
        return dt

    def separate_path(self, path):
        """
        Ex:
        path: 's3://bucket/folder0/folder1/key.csv'
        return
        bucket: 'bucket'
        key: 'folder0/folder1/key.csv'
        """
        path = path.strip().replace("s3://", "")
        bucket = path.strip().split("/")[0]
        key = "/".join(path.split("/")[1:])

        return bucket, key

    def get_diff_data_seconds(self, dt_before, dt_current=None):

        if dt_current is None:
            dt_current = datetime.strptime(self.date_time(), TIMESTAMP)
        else:
            dt_current = datetime.strptime(str(dt_current)[:19], TIMESTAMP)

        dt_before = str(dt_before)[:19]
        dt_before = datetime.strptime(dt_before, TIMESTAMP)
        seconds = (dt_current - dt_before).total_seconds()

        return seconds

    def convert_timestamp_epoch(self, add_days):

        dt_now = datetime.strptime(self.date_time(), TIMESTAMP)
        dt_new = dt_now + timedelta(days=int(add_days))
        dt_convert = int(time.mktime (dt_new.timetuple()))

        return dt_convert
