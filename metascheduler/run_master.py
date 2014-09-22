#!/usr/bin/env python
from master.metascheduler.main import app

app.run(host=app.config['HOSTNAME'])
