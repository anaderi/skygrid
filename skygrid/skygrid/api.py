from flask import jsonify
from flask.ext.restful import Resource

def api_decorator(f):
    def decorated(*args, **kwargs):
        # try:
        result = f(*args, **kwargs)
        if not result:
            result = {}
        return jsonify(**result)
        # except Exception, e:
        #     return jsonify(success=False, exception=str(e))

    return decorated


class SkygridResource(Resource):
    method_decorators = [api_decorator]
