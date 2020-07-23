import gzip
import time
from dnxdata.utils.utils import Utils
from dnxdata.logger import Logger
from dnxdata.resource import s3_client, s3_resource
from io import BytesIO


class S3:

    def __init__(self):
        self.utils = Utils()
        self.logger = Logger("DNX S3 =>")

    def get_object_s3(self, bucket, key, format_file=None):

        self.logger.debug("Starting get_object_s3")
        self.logger.debug("format {} {}/{}".format(format_file, bucket, key))

        file = s3_client.get_object(Bucket=bucket, Key=key)

        if format_file is not None:
            if format_file.lower() == "gz":
                _file = file['Body'].read()
                gzipfile = BytesIO(_file)
                decoded = gzip.decompress(
                    gzipfile.read()
                ).decode('utf-8')
        else:
            file = file['Body'].read()
            decoded = file.decode('utf-8')

        self.logger.debug("Finishing get_object_s3")

        return decoded

    def put_object_s3(self, bucket, key, file, format_file):

        self.logger.debug("Starting put_object_s3")
        self.logger.debug("Target {}/{}".format(bucket, key))

        if format_file.lower() == "gz":

            gz_body = BytesIO()
            gz = gzip.GzipFile(None, 'wb', 9, gz_body)
            # convert unicode strings to bytes
            gz.write(str(file).encode('utf-8'))
            gz.close()

            s3_client.put_object(
                Bucket=bucket,
                Body=gz_body.getvalue(),
                Key=key
            )

        self.logger.debug("Finishing put_object_s3")

    def copy_object_s3(self, bucket_ori, key_ori, bucket_dest, key_dest):

        self.logger.debug("Starting copy_object_s3")

        copy_source = {'Bucket': bucket_ori, 'Key': key_ori}

        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=bucket_dest.strip(),
            Key=key_dest.strip()
        )

        self.logger.debug("Finishing copy_object_s3")

    def delete_key(self, bucket, key):

        self.logger.debug("Starting delete_key")

        try:

            s3_resource.Object(bucket, key).delete()

            self.logger.debug("File deleted {}/{}".format(bucket, key))

        except Exception as e:
            self.logger.error("{}".format(e))

        self.logger.debug("Finishing delete_key")

    def move_file_s3(self, bucket_ori, key_ori, bucket_dest, key_dest):

        self.logger.debug("Starting move_file_s3")
        self.logger.debug(
            "Ori {}/{}  Dest {}/{}"
            .format(
                bucket_ori,
                key_ori,
                bucket_dest,
                key_dest
            )
        )

        self.copy_object_s3(bucket_ori, key_ori, bucket_dest, key_dest)

        equal_bucket = bucket_ori == bucket_dest
        equal_key = key_ori == key_dest

        if not equal_bucket or not equal_key:
            self.delete_key(bucket=bucket_ori, key=key_ori)

        self.logger.debug("Finishing move_file_s3")

    def get_list_file(self, bucket, filepath, endswith):

        self.logger.debug("Starting get_list_file")
        self.logger.debug("File {}/{}/*{}".format(bucket, filepath, endswith))

        if not filepath.endswith('/'):
            filepath += '/'

        prefix = filepath[1:] if filepath.startswith("/") else filepath
        _bucket = s3_resource.Bucket(bucket)

        keys_s3 = []
        for _ in _bucket.objects.filter(Prefix=prefix):
            if _.key.endswith(endswith):
                keys_s3.append("s3://" + str(bucket) + "/" + _.key)

        if len(keys_s3) == 0:
            self.logger.debug("0 file in bucket")
        else:
            for p in keys_s3:
                self.logger.debug("S3Keys {}".format(p))

        self.logger.debug("Finishing get_list_file")

        return keys_s3

    def get_list_parquet(self, path):

        self.logger.debug("Starting get_list_parquet")
        self.logger.debug("Target {}".format(path))

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

        self.logger.debug("Finishing get_list_parquet")

        return keys_s3

    def delete_file_s3(self, path, path_or_key="key"):

        self.logger.debug("Starting delete_file_s3")
        self.logger.debug("path {} path_or_key {}".format(path, path_or_key))

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
                        self.delete_key(bucket=_bucket, key=obj.key)

                elif path_or_key.lower() == "key":
                    self.delete_key(bucket=_bucket, key=_key)
            break

        self.logger.debug("Finishing delete_file_s3")
