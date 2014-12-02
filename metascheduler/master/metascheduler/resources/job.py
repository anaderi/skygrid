import json
from datetime import datetime

from flask import request
from api import MetaschedulerResource

import requests

from ..models import Job, JobStatus

def update_job(job, update_dict):
    if 'id' in update_dict:
        raise Exception('Could not update job id!')

    new_status = update_dict.get('status')
    if new_status and not new_status in JobStatus.valid_statuses:
        raise ValueError('Invalid status!')

    job.status = new_status

    new_descriptor = update_dict.get('descriptor')
    if new_descriptor:
        job.descriptor = new_descriptor

    job.save()

    if job.callback:
        r = requests.post(
            job.callback,
            data=json.dumps(job.to_dict()),
            headers={'content-type': 'application/json'}
        )


class JobResource(MetaschedulerResource):
    def get(self, job_id):
        if ',' in job_id:
            return {
              job_id: Job.objects.get(pk=job_id).to_dict() for job_id in job_id.split(',')
            }
        else:
            return Job.objects.get(pk=job_id).to_dict()

    def post(self, job_id):
        job = Job.objects.get(pk=job_id)
        update_dict = request.json

        update_job(job, update_dict)
        
        return {'updated_job': job.to_dict()}

    def delete(self, job_id):
        job = Job.objects.get(pk=job_id)
        job.delete()
