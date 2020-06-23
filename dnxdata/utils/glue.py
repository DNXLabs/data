import boto3
from dnxdata.utils.utils import Utils
from dnxdata.logger import info, error
from dnxdata.resource import glue_client


class Glue:

    def __init__(self):
        self.utils = Utils()

    def get_job_glue(self, job_name, job_run_id):
        info(
            "Starting _GetJobGlue job_name {},job_run_id {}"
            .format(
                job_name,
                job_run_id
            )
        )

        status = glue_client.get_job_run(JobName=job_name, RunId=job_run_id)

        info(
            "Finishing _GetJobGlue status {}"
            .format(status)
        )

        return status

    def get_status_job_glue(self, job_name, job_run_id):

        info(
            "Starting GetStatusJobGlue job_name {}, job_run_id {}"
            .format(
                job_name,
                job_run_id
            )
        )
        status = self.get_job_glue(job_name=job_name, job_run_id=job_run_id)
        state = status['JobRun']['JobRunState']

        info(
            "Finishing GetStatusJobGlue Status {}"
            .format(state)
        )

        return state

    def get_msg_error_job_glue(self, job_name, job_run_id):

        info(
            "Starting GetMsgErrorJobGlue job_name {}, job_run_id {}"
            .format(
                job_name,
                job_run_id
            )
        )
        status = self.get_job_glue(job_name=job_name, job_run_id=job_run_id)
        msg_error = status['JobRun']['ErrorMessage']

        info(
            "Finishing GetMsgErrorJobGlue ErrorMessage {}"
            .format(msg_error)
        )

        return msg_error
