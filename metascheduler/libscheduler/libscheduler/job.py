import os
import requests

class JobStatus:
    pending = "pending"
    running = "running"
    failed  = "failed"

    valid_statuses = set([pending, running, failed])


class JobAPI(object):
    """Class for communicating with metascheduler about Jobs"""
    def __init__(self, job_id):
        self.job_id = job_id

    def set_status(self, status):
        if not status in JobStatus.valid_statuses:
            raise Exception('invalid status')

        pass