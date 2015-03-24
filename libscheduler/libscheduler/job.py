import os
import json

from .common import *

class JobMS(object):
    """Class for communicating with metascheduler about Jobs"""
    def __init__(self, job_id, status='', descriptor={}, input=[], output=[],
            api_url="http://localhost:5000/", from_api=False, debug={}):
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
            self.descriptor = descriptor
            self.input = input
            self.output = output
            self._debug = {}

    def load_from_api(self):
        result = ms_get(self.job_url)

        self.status = result['status']
        self.descriptor = result['descriptor']
        self.input = result['input']
        self.output = result['output']


        return self


    def update_status(self, status):
        self.status = status

        return ms_post(
            os.path.join(self.job_url, 'status'),
            data=json.dumps({'status': status}),
            headers=JSON_HEADERS
        )

    def update_output(self, output):
        self.output = output

        return ms_post(
            os.path.join(self.job_url, 'output'),
            data=json.dumps({'output': output}),
            headers=JSON_HEADERS
        )

    def update_debug(self, debug):
        self._debug = debug

        return ms_post(
            os.path.join(self.job_url, 'debug'),
            data=json.dumps({'output': debug}),
            headers=JSON_HEADERS
        )


    def delete(self):
        return ms_delete(self.job_url)


    def json(self):
        return json.dumps({
            'job_id': self.job_id,
            'status': self.status,
            'descriptor': self.descriptor
        })
