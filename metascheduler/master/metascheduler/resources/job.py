import json
from datetime import datetime

from flask import request
from api import MetaschedulerResource

import requests

from ..models import Job, JobStatus

# def update_job(job, update_dict):
#     if 'id' in update_dict:
#         raise Exception('Could not update job id!')

#     new_status = update_dict.get('status')
#     if new_status:
#         assert new_status in JobStatus.valid_statuses
#         job.status = new_status

#     new_descriptor = update_dict.get('descriptor')
#     if new_descriptor:
#         job.descriptor = new_descriptor

#     job.save()

#     if job.callback:
#         r = requests.post(
#             job.callback,
#             data=json.dumps(job.to_dict()),
#             headers={'content-type': 'application/json'}
#         )


class JobResource(MetaschedulerResource):
    def get(self, job_id):
        if ',' in job_id:
            return {
              job_id: Job.objects.get(pk=job_id).to_dict() for job_id in job_id.split(',')
            }
        else:
            return Job.objects.get(pk=job_id).to_dict()

    def delete(self, job_id):
        job = Job.objects.get(pk=job_id)
        job.delete()


class JobStatusResource(MetaschedulerResource):
    def get(self, job_id):
        return {
            'status': Job.objects.get(pk=job_id).status
        }

    def post(self, job_id):
        update_dict = request.json
        new_status = update_dict.get('status')

        assert new_status in JobStatus.valid_statuses

        job = Job.objects.get(pk=job_id)
        job.status = new_status
        job.save()

        return {'updated_status': job.status}


class JobOutputResource(MetaschedulerResource):
    def get(self, job_id):
        return {
            'output': Job.objects.get(pk=job_id).output_files
        }

    def post(self, job_id):
        update_dict = request.json
        new_output = update_dict.get('output')

        job = Job.objects.get(pk=job_id)
        job.output_files = new_output
        job.save()

        return {'updated_output': job.output_files}


class JobInputResource(MetaschedulerResource):
    def get(self, job_id):
        return {
            'input_files': Job.objects.get(pk=job_id).input_files
        }
