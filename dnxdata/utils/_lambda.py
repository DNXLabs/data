from dnxdata.utils.boto3 import Boto3
from dnxdata.logger import info


class Lambda:

    def __init__(self):
        pass

    def invoke(self, name):
        info("Starting Invoke Lambda")
        s3 = Boto3()
        response = s3.invoke_lambda.invoke(
            FunctionName=name,
            InvocationType='Event'
        )

        if response.get("StatusCode") == 202:
            info("Invoke Lambda Success")
        else:
            info(
                "Failed Invoke Lambda {}"
                .format(response)
            )

        info("Finishing Invoke Lambda")
