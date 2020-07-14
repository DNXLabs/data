
# Mapping for dtypes mysql vs data frame pandas
mysql_vs_pandas = {
    "bigint": "bigint",
    "date": "datetime64",
    "datetime": "datetime64",
    "int": "int",
    "timestamp": "datetime64",
    "tinyint": "int",
    "smallint": "int",
    "varchar": "str"
}

mysql_vs_spark = {
    "bigint": "integer",
    "date": "timestamp",
    "datetime": "timestamp",
    "int": "integer",
    "timestamp": "timestamp",
    "tinyint": "integer",
    "smallint": "integer",
    "varchar": "string"
}
