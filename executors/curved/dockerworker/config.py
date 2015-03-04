import os
import imp

conf_file = os.environ.get('MC_WORKER_CONFIG')

if not conf_file:
    raise Exception("Environment variable $MC_WORKER_SETTINGS is not set.")

config = imp.load_source('config', conf_file)
