import gzip
import time
from dnxdata.utils.utils import Utils
from dnxdata.logger import Logger
from dnxdata.resource import s3_client, s3_resource
from io import BytesIO


class Boto3:

    def __init__(self):
        self.utils = Utils()
        self.logger = Logger("DNX Boto3 =>")

    def get_list_parquet(self, path):
        self.logger.info("Starting get_list_parquet")

        keys_s3 = []
        list_path = []

        v_boolean_list = True if isinstance(path, list) else False

        while True:
            if not v_boolean_list:
                if path.endswith('.parquet'):
                    keys_s3.append(path)
                    break
                else:
                    list_path.append(path)
            else:
                list_path = path

            for row in list_path:
                if row.endswith('.parquet'):
                    keys_s3.append(row)
                    continue
                source = self.utils.get_bucket_key(row)
                parquets = self.get_list_file(
                    bucket=source.get("bucket"),
                    filepath=source.get("key"),
                    endswith=".parquet"
                )
                for parquet in parquets:
                    keys_s3.append(parquet)
            break
        self.logger.info("Finishing get_list_parquet")
        return keys_s3

    def put_object_s3(self, bucket, key, file):

        self.logger.info("Starting put_object_s3")

        gz_body = BytesIO()
        gz = gzip.GzipFile(None, 'wb', 9, gz_body)
        gz.write(str(file).encode('utf-8'))  # convert unicode strings to bytes
        gz.close()
        # GzipFile has written the compressed bytes into our gz_body
        s3_client.put_object(
            Bucket=bucket,
            Key=key,  # Note: NO .gz extension!
            ContentType='text/plain',  # the original type
            ContentEncoding='gzip',  # MUST have or browsers will error
            Body=gz_body.getvalue()
        )

        self.logger.info("Finishing put_object_s3")

    def get_object_s3(self, bucket, key, format_file=None):

        self.logger.info(
            "Starting GetObjectS3 format {} {}/{}"
            .format(
                format_file,
                bucket,
                key
            )
        )

        file = s3_client.get_object(Bucket=bucket, Key=key)

        if format_file is not None:
            if format_file.lower() == "gz":
                bytestream = BytesIO(file['Body'].read())
                decoded = gzip.GzipFile(
                    None,
                    'rb',
                    fileobj=bytestream
                ).read().decode('utf-8')
        else:
            file = file['Body'].read()
            decoded = file.decode('utf-8')

        self.logger.info("Finishing GetObjectS3")

        return decoded

    def move_file_s3(self, bucket_ori, key_ori, bucket_dest, key_dest):
        self.logger.info(
            "Starting MoveFileS3 Ori {}/{}  Dest {}/{}"
            .format(
                bucket_ori,
                key_ori,
                bucket_dest,
                key_dest
            )
        )

        copy_source = {'Bucket': bucket_ori, 'Key': key_ori}
        self.logger.info("Starting Change Bucket")
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=bucket_dest.strip(),
            Key=key_dest.strip()
        )
        self.logger.info("Finishing Change Bucket")
        time.sleep(3)
        self.logger.info("Starting Delete File")
        s3_client.delete_object(
            Bucket=bucket_ori.strip(),
            Key=key_ori.strip()
        )
        self.logger.info("Finishing Delete File")

        self.logger.info("Finishing MoveFileS3")

    def _delete_key(self, bucket, key):

        v_count = 0
        while v_count < 3:
            v_count += 1
            try:
                s3_resource.Object(bucket, key).delete()
                time.sleep(1)
            except Exception as e:
                self.logger.error(e)
                pass

    def delete_file_s3(self, path, path_or_key="key"):

        self.logger.debug(
            "Starting DeleteFileS3 path {} path_or_key {}"
            .format(
                path,
                path_or_key
            )
        )

        while True:

            if not isinstance(path, list):
                path = path.split(" ")

            if len(path) == 0:
                self.logger.debug("0 path for delete")
                break

            bucket_aux = ""
            for row in path:
                _bucket, _key = self.utils.separate_path(path=row)
                if _bucket != bucket_aux:
                    bucket = s3_resource.Bucket(_bucket)
                    bucket_aux = _bucket

                if path_or_key.lower() == "path":
                    for obj in bucket.objects.filter(Prefix=_key):
                        self.logger.debug(
                            "File deleted {}/{}"
                            .format(
                                _bucket,
                                obj.key
                            )
                        )
                        self._delete_key(bucket=_bucket, key=obj.key)

                elif path_or_key.lower() == "key":
                    self.logger.debug(
                        "File deleted {}/{}"
                        .format(
                            _bucket,
                            _key
                        )
                    )
                    self._delete_key(bucket=_bucket, key=_key)
            break

        self.logger.debug("Finishing DeleteFileS3")

    def get_list_file(self, bucket, filepath, endswith):

        self.logger.debug(
            "Starting GetListFile {}/{}/*{}"
            .format(
                bucket,
                filepath,
                endswith
            )
        )

        if not filepath.endswith('/'):
            filepath += '/'

        """
        path = "{}/{}".format(bucket, filepath)
        desc = wr.s3.describe_objects(path, wait_time=30)
        S3keys = [key for key in desc if key.endswith(endswith)]
        This call above is problem.
        """
        prefix = filepath[1:] if filepath.startswith("/") else filepath
        _bucket = s3_resource.Bucket(bucket)

        keys_s3 = []
        for _ in _bucket.objects.filter(Prefix=prefix):
            if _.key.endswith(endswith):
                keys_s3.append(["s3://" + str(bucket) + "/" + _.key])

        if (len(keys_s3) == 0):
            self.logger.debug(
                "No {} found in bucket {}/{}"
                .format(
                    endswith,
                    bucket,
                    filepath
                )
            )
        else:
            for p in keys_s3:
                self.logger.debug("S3Keys {}".format(p))

        self.logger.debug("Finishing GetListFile")

        return keys_s3
