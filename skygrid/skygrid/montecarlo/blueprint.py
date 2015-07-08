from flask import Blueprint
from jinja2 import TemplateNotFound

from flask.ext import restful

blueprint = Blueprint('montecarlo', __name__)


from .resources import *


api = restful.Api(blueprint)

api.add_resource(MonteCarloList, '/montecarlo')
api.add_resource(MonteCarloDetail, '/montecarlo/<string:mc_id>')
api.add_resource(MonteCarloCallback, '/montecarlo/<string:mc_id>/callback')
api.add_resource(MonteCarloRefresh, '/montecarlo/<string:mc_id>/refresh')
api.add_resource(MonteCarloJobs, '/montecarlo/<string:mc_id>/jobs')