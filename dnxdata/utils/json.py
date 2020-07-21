from dnxdata.logger import Logger
from dnxdata.utils.dynamo import Dynamo


class Json:

    def __init__(self, table):
        self.logger = Logger("DNX Json =>")
        self.dynamo = Dynamo()
        self.table = table

    def load_json(self, key=None, value=None):

        try:
            self.logger.debug("Starting load_json")
            self.logger.debug("filter json key {} value {}".format(key, value))

            dict_load = self.dynamo.scan_table_all_pages(
                table=self.table,
                filter_key="key",
                filter_value=["config"]
            )

            dict_load = dict_load[0]["parameters"]

            if key is None:
                pass
            elif (key is not None) & (value is None):
                dict_load = dict_load[key]
            elif value is not None:
                dict_load = dict_load[key][value]

            self.logger.debug(dict_load)

            self.logger.debug("Finishing load_json")
            return dict_load

        except Exception as e:
            self.logger.error("Error load_json: {} ".format(e))

    def global_json(self, key=None):

        if key is None:
            return self.load_json(key="global")
        else:
            self.logger.debug("parameter {}".format(key))
            return self.load_json(key="global", value=key)

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

        self.logger.debug("Starting get_config")
        self.logger.debug(
            "database {} table {}"
            .format(
                database.upper(),
                table.upper()
            )
        )

        config = {}

        file_json = self.load_json()

        try:
            config = file_json["global"]
            self.logger.debug("global config {}".format(config))
        except Exception as e:
            self.logger.error("global config not configured")
            self.logger.error(e)
            exit(1)

        try:
            config_database = file_json["database"][database]["config"]
            config.update(config_database)
            self.logger.debug("database config {}".format(config_database))
        except Exception as e:
            self.logger.error("database config not configured")
            self.logger.error(e)
            exit(1)

        try:
            config_table = file_json["database"][database]["table"][table]
            config.update(config_table)
            config.update({"database_rds": database})
            self.logger.debug("table config {}".format(config_table))
        except Exception as e:
            self.logger.debug("table config not configured")
            self.logger.error(e)
            exit(1)

        self.logger.debug("complete merge config {}".format(config))
        self.logger.debug("Finishing get_config")

        return config
