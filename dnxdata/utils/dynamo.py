import time
from boto3.dynamodb.conditions import Key
from dnxdata.utils.utils import Utils
from dnxdata.resource import dynamo_resource
from dnxdata.logger import Logger


class Dynamo:

    def __init__(self):
        self.utils = Utils()
        self.logger = Logger("DNX Dynamo =>")

    def put_table_item(self, table, item, key, update=True):

        self.logger.info(
            "Starting PutTableItem Table {} DynamoDB Item {}"
            .format(
                table,
                item
            )
        )

        if update:
            item_get = self.get_item_table(table=table, key=key)
            if len(item_get) != 0:
                for key, value in item.items():
                    item_get.update({key: value})
            else:
                item_get = item
        else:
            item_get = item

        item_get.update({"timestamp": self.utils.date_time(milliseconds=True)})
        table_db = dynamo_resource.Table(table)
        response = table_db.put_item(Item=item_get)

        self.logger.debug(
            "Finishing PutTableItem Table {} DynamoDB Response {}"
            .format(
                table,
                response
            )
        )

        self.logger.info("Finishing PutTableItem")

        return response

    def get_item_table(self, table, key):

        self.logger.info(
            "Starting GetItemTable Table {} DynamoDB Key {}"
            .format(
                table,
                key
            )
        )
        table_db = dynamo_resource.Table(table)
        response = table_db.get_item(Key=key)

        result = {}
        if response.get("Item"):
            for key, value in response.get("Item").items():
                if key not in ['ResponseMetadata']:
                    result.update({key: value})

        self.logger.debug("{}".format(result))

        self.logger.info("Finishing GetItemTable")

        return result

    def delete_table_item(self, table, key):

        self.logger.info(
            "Starting DeleteTableItem Table {} DynamoDB Key {}"
            .format(
                table,
                key
            )
        )
        table_db = dynamo_resource.Table(table)
        response = table_db.delete_item(Key=key)

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            self.logger.info("Successful deletion")
            time.sleep(1)
            item = self.get_item_table(table=table, key=key)
            if len(item) > 1:
                self.logger.info("Double check exclusion table")
                time.sleep(1)
                response = table_db.delete_item(Key=key)

        self.logger.info(
            "Finishing DeleteTableItem Table {} DynamoDB Response {}"
            .format(
                table,
                response
            )
        )

        return response

    def update_table_item(self, table, key, updateExpression, expressionAttributeValues):

        try:
            self.logger.info(
                "Starting UpdateTableItem Table {} DynamoDB, Key {}, updateExpression {}, expressionAttributeValues {}"
                .format(
                    table,
                    key,
                    updateExpression,
                    expressionAttributeValues
                )
            )
            table_db = dynamo_resource.Table(table)

            response = table_db.update_item(
                Key=key,
                UpdateExpression=str(expressionAttributeValues),
                ExpressionAttributeValues=updateExpression,
                ReturnValues="UPDATED_NEW"
            )
            self.logger.info(
                "Finishing UpdateTableItem Table {} DynamoDB Response {}"
                .format(
                    table,
                    response
                )
            )
        except Exception as e:
            self.logger.error(
                "UpdateTableItem Table: {} Error: {}"
                .format(
                    table,
                    e
                )
            )
            return
        return response

    def get_data_dynamo_index(self, table, index_name, key, value):

        self.logger.info(
            "Starting GetDataIndex Table {} DynamoDB, IndexName {}, Key {}, Value {}"
            .format(
                table,
                index_name,
                key,
                value
            )
        )
        table = dynamo_resource.Table(table)
        response = table.query(
            IndexName=index_name,
            KeyConditionExpression=Key(key).eq(value))
        response = response['Items']

        self.logger.info(
            "Finishing GetDataIndex table {} DynamoDB Response {}"
            .format(
                table,
                response
            )
        )

        return response

    def move_data_for_another_table(self, key, list_update, table_ori, table_dest, delete_ori=True):

        self.logger.info(
            "Starting MoveDataForOtherTable Key {}, listUpdate {}, tableOri {},tableDest {}"
            .format(
                key,
                list_update,
                table_ori,
                table_dest
            )
        )
        item = self.get_item_table(table=table_ori, key=key)

        if len(item) != 0:
            self.logger.info("MoveDataForOtherTable Line Log StageControl")

            for key, value in list_update.items():
                item.update({key: value})

            response = self.put_table_item(
                table=table_dest,
                item=item,
                key=key,
                update=False
            )
            self.logger.info(
                "MoveDataForOtherTable Response PutTableItem {}"
                .format(
                    response
                )
            )

            if not response and delete_ori:
                time.sleep(2)
                response = self.delete_table_item(
                    table=table_ori,
                    key=key
                )
                self.logger.info(
                    "MoveDataForOtherTable Response DeleteTableItem {}"
                    .format(
                        response
                    )
                )
            else:
                self.logger.info(
                    "self.logger.infodelete_ori {} "
                    .format(delete_ori))
                self.logger.info(
                    "MoveDataForOtherTable Invalid Response"
                )
        else:
            self.logger.info("MoveDataForOtherTable Invalid GetItemTable")

        self.logger.info("Finishing MoveDataForOtherTable")

    def scan_table_all_pages(self, table, filter_key=None, filter_value=None):

        self.logger.info(
            "Starting ScanTableAllPages Table {},filter_key {},filter_value {}"
            .format(
                table,
                filter_key,
                filter_value
            )
        )

        table = dynamo_resource.Table(table)
        items = []

        if filter_key and filter_value:
            if not isinstance(filter_value, list):
                self.logger.info(
                    "ScanTableAllPages Parameter invalid {}, required list []"
                    .format(filter_value))
                filter_value = filter_value.split(",")

            for row in filter_value:
                filtering_exp = Key(filter_key).eq(row)
                response = table.scan(FilterExpression=filtering_exp)

                items += response['Items']
                while True:
                    if response.get('LastEvaluatedKey'):
                        response = table.scan(
                            ExclusiveStartKey=response['LastEvaluatedKey']
                        )
                        items += response['Items']
                    else:
                        break

        else:
            response = table.scan()
            if len(response) != 0:
                items += response['Items']
                while True:
                    if response.get('LastEvaluatedKey'):
                        response = table.scan(
                            ExclusiveStartKey=response['LastEvaluatedKey']
                        )
                        items += response['Items']
                    else:
                        break

        self.logger.info(
            "ScanTableAllPages {}"
            .format(
                len(items)
            )
        )
        self.logger.debug(
            "Items Return ScanTableAllPages {}"
            .format(
                items
            )
        )

        self.logger.info("Finishing ScanTableAllPages")

        return items
