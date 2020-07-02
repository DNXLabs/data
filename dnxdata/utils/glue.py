from dnxdata.utils.utils import Utils
from dnxdata.logger import Logger
from dnxdata.resource import glue_client


class Glue:

    def __init__(self):
        self.utils = Utils()
        self.logger = Logger("DNX Glue =>")

    def get_job_glue(self, job_name, job_run_id):

        self.logger.debug(
            "Starting _GetJobGlue job_name {},job_run_id {}"
            .format(
                job_name,
                job_run_id
            )
        )

        status = glue_client.get_job_run(JobName=job_name, RunId=job_run_id)

        self.logger.debug(
            "Finishing _GetJobGlue status {}"
            .format(status)
        )

        return status

    def get_status_job_glue(self, job_name, job_run_id):

        self.logger.debug(
            "Starting GetStatusJobGlue job_name {}, job_run_id {}"
            .format(
                job_name,
                job_run_id
            )
        )
        status = self.get_job_glue(job_name=job_name, job_run_id=job_run_id)
        state = status['JobRun']['JobRunState']

        self.logger.debug(
            "Finishing GetStatusJobGlue Status {}"
            .format(state)
        )

        return state

    def get_msg_error_job_glue(self, job_name, job_run_id):

        self.logger.debug(
            "Starting GetMsgErrorJobGlue job_name {}, job_run_id {}"
            .format(
                job_name,
                job_run_id
            )
        )
        status = self.get_job_glue(job_name=job_name, job_run_id=job_run_id)
        msg_error = status['JobRun']['ErrorMessage']

        self.logger.debug(
            "Finishing GetMsgErrorJobGlue ErrorMessage {}"
            .format(msg_error)
        )

        return msg_error
