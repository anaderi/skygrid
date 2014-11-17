from .queue import QueueMS
from .job import JobMS


class Metascheduler(object):
    def __init__(self, api_url):
        self.api_url = api_url

    def queue(self, queue_name, **kwargs):
        return QueueMS(queue_name, api_url=self.api_url, **kwargs)

    def job(self, job_id, **kwargs):
        return JobMS(job_id, api_url=self.api_url, **kwargs)
