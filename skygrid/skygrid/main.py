from .app import *
from .models import *


if app.config['DB_USE_AUTH']:
    connect(app.config['MONGO_DB'], username=app.config['MONGO_DB_USERNAME'], password=app.config['MONGO_DB_PASSWORD'])
else:
    connect(app.config['MONGO_DB'])



from flask.ext import restful

from .resources import (
    DatasetList,
    DatasetDetail
)


api = restful.Api(app)

api.add_resource(DatasetList, '/datasets')
api.add_resource(DatasetDetail, '/datasets/<string:ds_id>')
