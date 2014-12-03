from flask import Blueprint
from jinja2 import TemplateNotFound

from flask.ext import restful

blueprint = Blueprint('classifiers', __name__)


from .resources import *


api = restful.Api(blueprint)

api.add_resource(ClassifierList, '/classifiers')
api.add_resource(ClassifierDetail, '/classifiers/<string:cl_id>')
api.add_resource(ClassifierCallback, '/classifiers/<string:cl_id>/callback')