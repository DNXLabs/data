import pymysql
from dnxdata.logger import Logger


class Mysql:

    def __init__(self):
        self.logger = Logger("DNX Mysql =>")

    def execute(self, connection_settings, script):

        self.logger.debug(
            "Starting Exec Query Mysql Script {}"
            .format(script)
        )

        conn = self.connection(connection_settings=connection_settings)

        result = []
        with conn.cursor() as cur:
            cur.execute(script)
            conn.commit()
            cur.close()
            for row in cur:
                result.append(list(row))

        self.logger.debug("Return Mysql {}".format(result))
        self.logger.debug("Finishing Exec Query Mysql")
        return result

    def connection(self, connection_settings):

        self.logger.debug("Starting Connection Mysql")

        conn = pymysql.connect(
            host=connection_settings.get("host"),
            user=connection_settings.get("user"),
            passwd=connection_settings.get("passwd"),
            db=connection_settings.get("db"),
            connect_timeout=5
        )

        self.logger.debug("Finishing Connection Mysql")
        return conn

    def get_primary_key(self, connection_settings, schema, table):

        self.logger.debug(
            "Starting get_primary_key schema {} table {}"
            .format(
                schema,
                table
            )
        )

        select = """
        SELECT column_name
          FROM self.logger.information_schema.columns
          WHERE lower(table_schema) = "{}"
            AND lower(table_name) = "{}"
            AND COLUMN_KEY = "PRI"
          ORDER BY ORDINAL_POSITION """.format(schema.lower(), table.lower())

        self.logger.debug("Select get_primary_key {}".format(select))

        result = self.execute(
            connection_settings=connection_settings,
            script=select
        )

        result = []
        for x in result[0]:
            result.append(x)

        self.logger.debug("Result {}".format(result))
        self.logger.debug("Finishing get_primary_key")

        return result
