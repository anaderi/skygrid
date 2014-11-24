from flask import jsonify, current_app
from flask.ext.restful import Resource

import traceback

def api_decorator(f):
    def decorated(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            if not result:
                result = {}

            return jsonify(success=True, data=result)
        except Exception, e:
            d = {'success': False}

            if current_app.config['DEBUG']:
                d['traceback'] = traceback.format_exc()
                d['exception'] = str(e)

            return jsonify(d)

    return decorated


class SkygridResource(Resource):
    method_decorators = [api_decorator]
