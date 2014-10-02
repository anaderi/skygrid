import os
import requests
import json

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
        result = requests.get(self.job_url).json()
        self._check_server_result(result)

        self.status = result['status']
        self.description = result['description']

        return self


    def _check_server_result(self, result):
        if result['success']:
            return True
        else:
            message = "Error on server side: " + result['exception']
            raise Exception(message)

    def _post_update(self, update_dict):
        r = requests.post(self.job_url, data=json.dumps(update_dict))
        result = r.json()

        return self._check_server_result(result)

    def update_status(self, status):
        return self._post_update({'status': status})

    def update_description(self, description):
        return self._post_update({'description': description})

    def delete(self):
        result = requests.delete(self.job_url).json()
        return  self._check_server_result(result)
