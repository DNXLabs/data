import dateutil.tz
from datetime import datetime
from dnxdata.logger import Logger


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
        self.logger.debug(
            "Get Bucket key source {}"
            .format(source)
        )
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
