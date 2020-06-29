from dnxdata.resource import lambda_client
from dnxdata.logger import Logger
import json


class Lambda:

    def __init__(self):
        self.logger = Logger("DNX Lambda =>")

    def invoke(self, name, pay_load=None):
        self.logger.debug("Starting Invoke Lambda")
        response = lambda_client.invoke(
            FunctionName=name,
            InvocationType='Event',
            Payload=json.dumps(pay_load)
        )

        if response.get("StatusCode") == 202:
            self.logger.debug("Invoke Lambda Success")
        else:
            self.logger.debug(
                "Failed Invoke Lambda {}"
                .format(response)
            )

        self.logger.debug("Finishing Invoke Lambda")
