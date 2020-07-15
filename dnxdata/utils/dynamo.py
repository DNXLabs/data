import time
from boto3.dynamodb.conditions import Key
from dnxdata.utils.utils import Utils
from dnxdata.resource import dynamo_resource
from dnxdata.logger import Logger


class Dynamo:

    def __init__(self):
        self.utils = Utils()
        self.logger = Logger("DNX Dynamo =>")

    def put_table_item(self, table, item, key, field_update="timestamp", update=True):

        self.logger.debug("Starting put_table_item")
        self.logger.debug(
            "Table {} DynamoDB Item {}"
            .format(
                table,
                item
            )
        )

        if update:
            item_get = self.get_table_item(table=table, key=key)
            if len(item_get) != 0:
                for _key, _value in item.items():
                    item_get.update({_key: _value})
            else:
                item_get = item
        else:
            item_get = item

        item_get.update(
            {
                field_update: self.utils.date_time(milliseconds=True)
            }
        )
        table_db = dynamo_resource.Table(table)
        response = table_db.put_item(Item=item_get)

        self.check_response(response)

        self.logger.debug("Finishing put_table_item")

        return response

    def get_table_item(self, table, key):

        self.logger.debug("Starting get_table_item")
        self.logger.debug(
            "Table {} DynamoDB Key {}"
            .format(
                table,
                key
            )
        )

        table_db = dynamo_resource.Table(table)
        response = table_db.get_item(Key=key)

        result = {}
        Item = response.get("Item", None)
        if Item is not None:
            for _key, _value in Item.items():
                result.update({_key: _value})

        self.logger.debug("{}".format(result))

        self.logger.debug("Finishing get_table_item")

        return result

    def delete_table_item(self, table, key):

        self.logger.debug("Starting delete_table_item")
        self.logger.debug(
            "Table {} DynamoDB Key {}"
            .format(
                table,
                key
            )
        )

        table_db = dynamo_resource.Table(table)
        response = table_db.delete_item(Key=key)
        self.check_response(response)

        time.sleep(1)
        self.logger.debug("Double check exclusion line table")
        item = self.get_table_item(table=table, key=key)
        if len(item) > 0:
            time.sleep(1)
            response = table_db.delete_item(Key=key)
            self.check_response(response)

        self.logger.debug("Finishing delete_table_item")

        return response

    def get_data_dynamo_index(self, table, index_name, key, value):

        self.logger.debug("Starting get_data_dynamo_index")
        self.logger.debug(
            "Table {} DynamoDB, IndexName {}, Key {}, Value {}"
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
        self.check_response(response)

        self.logger.debug("Finishing get_data_dynamo_index")

        return response

    def move_data_for_another_table(self, key, list_update, table_ori, table_dest, delete_ori=True):

        self.logger.debug("Starting move_data_for_another_table")
        self.logger.debug(
            "Key {}, tableOri {}, tableDest {}, delete_ori {}, listUpdate {}"
            .format(
                key,
                table_ori,
                table_dest,
                delete_ori,
                list_update
            )
        )

        item = self.get_table_item(table=table_ori, key=key)

        if len(item) != 0:
            self.logger.debug("Moving line for table StageControlLog")

            for _key, value in list_update.items():
                item.update({_key: value})

            response = self.put_table_item(
                table=table_dest,
                item=item,
                key=key,
                update=False
            )

            v_success = self.check_response(response)

            if v_success and delete_ori:
                time.sleep(2)
                self.delete_table_item(table=table_ori, key=key)
            else:
                self.logger.debug("delete_ori {} ".format(delete_ori))
        else:
            self.logger.debug("Invalid GetItemTable")

        self.logger.debug("Finishing move_data_for_another_table")

    def scan_table_all_pages(self, table, filter_key=None, filter_value=None):

        self.logger.debug("Starting scan_table_all_pages")
        self.logger.debug(
            "Table {},filter_key {},filter_value {}"
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
                self.logger.debug(
                    "Parameter invalid {}, required list []"
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

        self.logger.debug("Count of lines returned {}".format(len(items)))
        self.logger.debug("Items Return {}".format(items))

        self.logger.debug("Finishing scan_table_all_pages")

        return items

    def check_response(self, response):

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            self.logger.debug("Successful")
        else:
            self.logger.error("Response {}".format(response))
            return False

        return True
