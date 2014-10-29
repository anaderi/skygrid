import json
from time import time

from flask import request
from api import MetaschedulerResource

from ..models import db, Job, JobStatus


def check_job_update_valid(update_dict):
    if 'id' in update_dict:
        raise Exception('Could not update job id!')

    new_status = update_dict.get('status')
    if new_status and not new_status in JobStatus.valid_statuses:
        raise ValueError('Invalid status!')


class JobResource(MetaschedulerResource):
    def _get_job(self, job_id):
        return Job.query.filter(Job.job_id == job_id).first()


    def get(self, job_id):
        if ',' in job_id:
            id_list = job_id.split(',')
            jobs = Job.query.filter(Job.job_id.in_(id_list))

            return {
                job.job_id: job.to_dict() for job in jobs
            }
        else:
            return self._get_job(job_id).to_dict() 


    def post(self, job_id):
        update_dict = json.loads(request.data)
        check_job_update_valid(update_dict)
        update_dict['last_update'] = time()

        job = self._get_job(job_id)

        job.query.update(update_dict)
        db.session.commit()

        return {'updated_job': job.to_dict()}


    def delete(self, job_id):
        job = self._get_job(job_id)
    
        db.session.delete(job)
        db.session.commit()
