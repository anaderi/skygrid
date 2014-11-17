#!/usr/bin/env python
from skygrid.main import app

app.run(host=app.config['HOSTNAME'], port=6000)
