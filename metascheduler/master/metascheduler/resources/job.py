import json
from time import time

from flask import request
from api import MetaschedulerResource

from ..models import Job, JobStatus
from libscheduler.job import check_job_update_valid


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
        job = Job.objects.get(pk=job_id)
        return job.to_dict()

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

