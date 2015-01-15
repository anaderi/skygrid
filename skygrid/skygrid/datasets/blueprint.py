from flask import Blueprint
from jinja2 import TemplateNotFound

from flask.ext import restful

blueprint = Blueprint('datasets', __name__)


from .resources import (
    DatasetList,
    DatasetDetail
)


api = restful.Api(blueprint)

api.add_resource(DatasetList, '/datasets')
api.add_resource(DatasetDetail, '/datasets/<string:ds_id>')
