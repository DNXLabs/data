import pymysql
from dnxdata.logger import Logger
from dnxdata.utils.mapping import mysql_vs_pandas


class Mysql:

    def __init__(self):
        self.logger = Logger("DNX Mysql =>")

    def execute(self, connection_settings, script):

        self.logger.debug("Starting execute")
        self.logger.debug("{}".format(script))

        conn = self.connection(connection_settings=connection_settings)

        result = []
        with conn.cursor() as cur:
            cur.execute(script)
            conn.commit()
            cur.close()
            for row in cur:
                result.append(list(row))

        self.logger.debug("Result {}".format(result))

        self.logger.debug("Finishing execute")

        return result

    def connection(self, connection_settings):

        self.logger.debug("Starting connection")

        conn = pymysql.connect(
            host=connection_settings.get("host"),
            user=connection_settings.get("user"),
            passwd=connection_settings.get("passwd"),
            db=connection_settings.get("db"),
            connect_timeout=5
        )

        self.logger.debug("Finishing connection")

        return conn

    def get_primary_key(self, connection_settings, schema, table):

        self.logger.debug("Starting get_primary_key")
        self.logger.debug("Schema {} table {}".format(schema, table))

        select = """
        SELECT column_name
          FROM information_schema.columns
          WHERE lower(table_schema) = "{}"
            AND lower(table_name) = "{}"
            AND COLUMN_KEY = "PRI"
          ORDER BY ORDINAL_POSITION """.format(schema.lower(), table.lower())

        result = self.execute(
            connection_settings=connection_settings,
            script=select
        )

        primary = []
        if result:
            for x in result[0]:
                primary.append(x)

        self.logger.debug("Result {}".format(primary))

        self.logger.debug("Finishing get_primary_key")

        return primary

    def get_list_dtypes(self, connection_settings, schema, table):

        self.logger.debug("Starting get_list_data_type")
        self.logger.debug(
            "schema {} table {}"
            .format(
                schema.upper(),
                table.upper()
            )
        )

        select = """
        SELECT COLUMN_NAME, DATA_TYPE
        FROM information_schema.columns
        WHERE lower(table_schema) = "{}"
            AND lower(table_name) = "{}"
        ORDER BY ORDINAL_POSITION """.format(schema.lower(), table.lower())

        result = self.execute(
            connection_settings=connection_settings,
            script=select
        )
        result = {key: value for key, value in result}

        self.logger.debug("List DataType {}".format(result))

        self.logger.debug("Finishing get_list_data_type")

        return result
