import os
import json

from .common import *

class JobMS(object):
    """Class for communicating with metascheduler about Jobs"""
    def __init__(self, job_id, status='', description={}, api_url="http://localhost:5000/", from_api=False):
        self.job_id = job_id
        self.job_url = os.path.join(
            api_url,
            'jobs',
            self.job_id
        )

        if from_api:
            self.load_from_api()
        else:
            self.status = status
            self.description = description

    def load_from_api(self):
        result = ms_get(self.job_url)

        self.status = result['status']
        self.description = result['description']

        return self


    def _post_update(self, update_dict):
        return ms_post(self.job_url, data=json.dumps(update_dict))


    def update_status(self, status):
        return self._post_update({'status': status})


    def update_description(self, description):
        return self._post_update({'description': description})


    def delete(self):
        return ms_delete(self.job_url)
