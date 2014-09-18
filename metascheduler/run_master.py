#!/usr/bin/env python
from master.frontend.main import app

app.run(host=app.config['HOSTNAME'])
