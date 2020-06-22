import boto3
import uuid
from src.lib.logger import info, debug, error


class Kinesis:

    def __init__(self, name, region):
        self.name = name
        self.region = region

    def conn(self):

        info("Starting Conn Kinesis name {}, region {}".format(self.name, self.region))

        if self.region and self.name:

            self.client = boto3.client('firehose', region_name=self.region)
            self.stream = self.name.format(uuid.uuid4())

            self.kinesis = {"client": self.client,
                            "stream": self.stream}

            info("Finishing Conn Kinesis")
            return self.kinesis
        else:
            info("Invalid argument Conn Kinesis")
            exit(1)

    def send_data(self, data_binary_string, put_record="PRB", verbose=False):

        if verbose:
            info("Starting SendData Kinesis")

        option = ["PR", "PRB"]
        if put_record not in option:
            error("Put record not configure. Available {}".format(option))
            exit(1)

        if put_record == "PR":

            data_string = str(data_binary_string)
            data_binary_string = str.encode(data_string)
            response = self.client.put_record(
                DeliveryStreamName=self.stream,
                Record={'Data': data_binary_string}
            )

        elif put_record == "PRB":

            data_string = str(data_binary_string) + "\n"
            data_binary_string = str.encode(data_string)
            response = self.client.put_record_batch(
                DeliveryStreamName=self.stream,
                Records=[{'Data': data_binary_string}]
            )

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            debug("SUCCESS, your request ID is : " + response["ResponseMetadata"]["RequestId"])

        else:
            info("ERROR : something went wrong")
            exit(1)

        if verbose:
            info("Finishing SendData Kinesis")
