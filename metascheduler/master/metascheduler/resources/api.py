from flask import jsonify
from flask.ext.restful import Resource

from ..models import db, Queue

def api_decorator(f):
    def decorated(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            if not result:
                result = {}
            return jsonify(success=True, **result)
        except Exception, e:
            return jsonify(success=False, exception=str(e))

    return decorated


class MetaschedulerResource(Resource):
    method_decorators = [api_decorator]



def queue_exists(job_type):
    return db.session.query(Queue).filter(Queue.job_type==job_type).count() == 1


def queue_exists_decorator(f):
    def decorated(job_type, *args, **kwargs):
        if queue_exists(job_type):
            return f(job_type, *args, **kwargs)
        else:
            raise Exception('Queue does not exist')

    return decorated


class ExistingQueueResource(Resource):
    method_decorators = [queue_exists_decorator, api_decorator]
