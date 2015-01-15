#!/usr/bin/env python
from skygrid.app import app

app.run(host=app.config['HOSTNAME'], port=app.config['PORT'])
