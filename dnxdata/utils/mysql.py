import pymysql
from dnxdata.logger import info


class Mysql:

    def __init__(self):
        pass

    def execute(self, connection_settings, script):

        info(
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

        info("Return Mysql {}".format(result))
        info("Finishing Exec Query Mysql")
        return result

    def connection(self, connection_settings):

        info("Starting Connection Mysql")

        conn = pymysql.connect(
            host=connection_settings.get("host"),
            user=connection_settings.get("user"),
            passwd=connection_settings.get("passwd"),
            db=connection_settings.get("db"),
            connect_timeout=5
        )

        info("Finishing Connection Mysql")
        return conn

    def get_primary_key(self, connection_settings, schema, table):

        info(
            "Starting get_primary_key schema {} table {}"
            .format(schema, table)
        )

        select = """
        SELECT column_name
          FROM information_schema.columns
          WHERE lower(table_schema) = "{}"
            AND lower(table_name) = "{}"
            AND COLUMN_KEY = "PRI"
          ORDER BY ORDINAL_POSITION """.format(schema.lower(), table.lower())

        info(
            "Select get_primary_key {}"
            .format(select)
        )

        result = self.execute(
            connection_settings=connection_settings,
            script=select
        )

        # TODO Review logic
        result = [x for x in result[0]]

        info("Result {}".format(result))
        info("Finishing get_primary_key")

        return result
