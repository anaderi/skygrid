import os
from .queue import QueueMS
from .job import JobMS
from .common import ms_get, MetaschedulerServerError

class Metascheduler(object):
    def __init__(self, api_url):
        self.api_url = api_url
        self.status_url = os.path.join(self.api_url, 'status')
        try:
            alive = ms_get(self.status_url)
        except Exception, e:
            raise MetaschedulerServerError('Could not access Metascheduler on {}'.format(self.api_url))

    def queue(self, queue_name, **kwargs):
        return QueueMS(queue_name, api_url=self.api_url, **kwargs)

    def job(self, job_id, **kwargs):
        return JobMS(job_id, api_url=self.api_url, **kwargs)

    def get_statuses(self, job_id_list):
        url = os.path.join(self.api_url, 'jobs', ','.join(job_id_list), 'status')
        ret = ms_get(url)
        del ret['success']

        if len(job_id_list) == 1:
            return {job_id_list[0]: ret['status']}
        else:
            return {job_id: v['status'] for job_id, v in ret.items()}
