import json
from time import time

from flask import request

from ..models import Job, JobStatus
from api import MetaschedulerResource


class JobResource(MetaschedulerResource):
    def get(self, job_id):
        job = Job.objects.get(pk=job_id)
        return {'jobs': job.to_dict()}


    def check_update_valid(self, update_dict):
        if 'id' in update_dict:
            raise Exception('Could not update job id!')
        
        new_status = update_dict.get('status')
        if new_status and not new_status in JobStatus.valid_statuses:
            raise Exception('Invalid status!')



    def post(self, job_id):
        job = Job.objects.get(pk=job_id)
        update_dict = json.loads(request.data)

        self.check_update_valid(update_dict)
        
        for k, v in update_dict:
            job[k] = v

        job.last_update = time()
        job.save()

        return {'updated_job': job.to_dict()}
