import json

from src.lib.logger import info, debug, error
from src.lib.utils.boto3 import Boto3


class Json:

    def __init__(self, bucket_stage_artifacts):
        self.bucket_stage_artifacts = bucket_stage_artifacts

    def load_json(self, key=None, value=None):

        try:
            info("Starting LoadJson File Json Key {} Value {}".format(key, value))
            bucket = self.bucket_stage_artifacts
            key_s3 = "json/param_lambda.json"

            s3 = Boto3()
            file_json = s3.get_object_s3(bucket, key_s3)
            config_dict = json.loads(file_json)
            dict_load = config_dict

            if key is None:
                pass
            elif (key is not None) & (value is None):
                dict_load = dict_load[key]
            elif value is not None:
                dict_load = dict_load[key][value]

            info("Finishing LoadJson File Json")
            print(dict_load)
            return dict_load

        except Exception as e:
            error(
                "Error Load File Json: {} "
                .format(e)
            )

    def valid_key(self, key, value=None, table=None):

        info("Starting ValidKey Key {} Value {} Table {}".format(key, value, table))

        dict_file = self.load_json(key=key, value=value)

        v_boolean = True if (table.upper() in dict_file.keys()) | (table.lower() in dict_file.keys()) else False

        if not v_boolean:
            info("Non-parameterized File the Json")

        info("Finishing ValidKey Key File Json")

        return v_boolean

    def get_config(self, database, table):

        table = table.upper()
        database = database.lower()

        info("Starting get_config Json Database {} Table {}".format(database, table))

        config_default = {}

        file_json = self.load_json()

        try:
            config_default = file_json["param"]
            info("Config Param {}".format(config_default))
        except Exception as e:
            error("Config Param not configured")
            error(e)
            exit(1)

        try:
            config_default_aux = file_json["database"][database]["config"]
            config_default.update(config_default_aux)
            info("Config Default Database {}".format(config_default_aux))
        except Exception as e:
            error(
                "Config Default not configured for the database {} table {}"
                .format(
                    database,
                    table
                )
            )
            error(e)
            exit(1)

        try:
            config_default_aux = file_json["database"][database]["table"][table]
            config_default.update(config_default_aux)
            config_default.update({"database_rds": database})

            info(
                "Config Default Table {}"
                .format(config_default_aux)
            )
            info(
                "Complete config, default and exception {}"
                .format(config_default)
            )
        except Exception as e:
            debug(
                "Error Return Config Default {}"
                .format(str(e))
            )

        info(
            "Return Config {}"
            .format(config_default)
        )

        return config_default
