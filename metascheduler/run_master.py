#!/usr/bin/env python
from metascheduler.main import app

app.run(host=app.config['HOSTNAME'])
