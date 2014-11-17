import json
from time import time

from flask import request
from api import MetaschedulerResource

from ..models import Job, JobStatus

def check_job_update_valid(update_dict):
    if 'id' in update_dict:
        raise Exception('Could not update job id!')

    new_status = update_dict.get('status')
    if new_status and not new_status in JobStatus.valid_statuses:
        raise ValueError('Invalid status!')


from mongoengine import fields

def update_document(document, data_dict):

    def field_value(field, value):

        if field.__class__ in (fields.ListField, fields.SortedListField):
            return [
                field_value(field.field, item)
                for item in value
            ]
        if field.__class__ in (
            fields.EmbeddedDocumentField,
            fields.GenericEmbeddedDocumentField,
            fields.ReferenceField,
            fields.GenericReferenceField
        ):
            return field.document_type(**value)
        else:
            return value

    [setattr(
        document, key,
        field_value(document._fields[key], value)
    ) for key, value in data_dict.items()]

    return document


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
        update_dict = json.loads(request.data)

        check_job_update_valid(update_dict)
        update_document(job, update_dict)

        job.last_update = time()
        job.save()

        return {'updated_job': job.to_dict()}

    def delete(self, job_id):
        job = Job.objects.get(pk=job_id)
        job.delete()

