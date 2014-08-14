from time import time

from flask import request, jsonify

from .main import app
from ..generic.models import Worker



@app.route('/')
def index():
    return "Hello, world!"


@app.route('/beat/<int:wid>')
def worker_heartbeat(wid):
    worker, created = Worker.objects.get_or_create(
        wid=wid, 
        defaults={
            'hostname': request.remote_addr,
            'last_seen': time(),
            'meta': {}
        }
    )

    if not created:
        worker.last_seen = time()
        worker.save()

    return str(worker) + "\n"