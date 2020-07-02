from dnxdata.logger import Logger
from dnxdata.utils.dynamo import Dynamo
from dnxdata.utils.environments import DDB_CONFIG


class Json:

    def __init__(self):
        self.logger = Logger("DNX Json =>")
        self.dynamo = Dynamo()

    def load_json(self, key=None, value=None):

        try:
            self.logger.debug(
                "Starting LoadJson File Json Key {} Value {}"
                .format(
                    key,
                    value
                )
            )

            dict_load = self.dynamo.scan_table_all_pages(
                table=DDB_CONFIG,
                filter_key="key",
                filter_value=["config"]
            )

            dict_load = dict_load[0]["param"]

            if key is None:
                pass
            elif (key is not None) & (value is None):
                dict_load = dict_load[key]
            elif value is not None:
                dict_load = dict_load[key][value]

            self.logger.debug(dict_load)
            self.logger.debug("Finishing LoadJson File Json")

            return dict_load

        except Exception as e:
            self.logger.error(
                "Error Load File Json: {} "
                .format(e)
            )

    def valid_key(self, key, value=None, table=None):

        self.logger.debug(
            "Starting ValidKey Key {} Value {} Table {}"
            .format(
                key,
                value,
                table
            )
        )

        dict_file = self.load_json(key=key, value=value)

        equal_upper = table.upper() in dict_file.keys()
        equal_lower = table.lower() in dict_file.keys()

        if equal_upper or equal_lower:
            v_boolean = True
        else:
            v_boolean = False

        if not v_boolean:
            self.logger.debug("Non-parameterized File the Json")

        self.logger.debug("Finishing ValidKey Key File Json")

        return v_boolean

    def get_config(self, database, table):

        table = table.upper()
        database = database.lower()

        self.logger.debug(
            "Starting get_config Json Database {} Table {}".format(
                database,
                table
            )
        )

        config_default = {}

        file_json = self.load_json()

        try:
            config_default = file_json["global"]
            self.logger.debug("Config global {}".format(config_default))
        except Exception as e:
            self.logger.error("Config global not configured")
            self.logger.error(e)
            exit(1)

        try:
            config_default_aux = file_json["database"][database]["config"]
            config_default.update(config_default_aux)
            self.logger.debug(
                "Config database {}"
                .format(
                    config_default_aux
                )
            )
        except Exception as e:
            self.logger.error(
                "Config Default not configured for the database {} table {}"
                .format(
                    database,
                    table
                )
            )
            self.logger.error(e)
            exit(1)

        try:
            config_aux = file_json["database"][database]["table"][table]
            config_default.update(config_aux)
            config_default.update({"database_rds": database})

            self.logger.debug(
                "Config table {}"
                .format(config_aux)
            )
        except Exception as e:
            self.logger.debug(
                "Error Return Config Default {}"
                .format(str(e))
            )
            exit(1)

        self.logger.debug(
            "Return global, database and table {}"
            .format(config_default)
        )

        return config_default
