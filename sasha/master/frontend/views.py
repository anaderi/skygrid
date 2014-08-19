import json
from time import time

from flask import request, jsonify

from .main import app
from ..generic.models import Worker, Task, User


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


@app.route('/add_task', methods=['POST'])
def add_task():
    try:
        task_dict = json.loads(request.data)
        task_dict['owner'] = User.objects.get(username=task_dict['owner'])

        t = Task(**task_dict)
        t.save()

        return jsonify(success=True)
    except Exception, e:
        return jsonify(success=False, exception=str(e))


@app.route('/get_task', methods=['GET'])
def get_task():
    try:
        worker = Worker.objects.get(wid=int(request.args.get('wid')))
        n_task = int(request.args.get('ntask')) or 1 # how many tasks we need to return

        jsoned_tasks = []

        tasks = Task.objects(assigned_worker=None)[:n_task]
        print len(tasks)
        for task in tasks:
            task.assigned_worker = worker
            jsoned_tasks.append(task.to_json())

            task.save()

        return jsonify(success=True, tasks=jsoned_tasks)


    except Exception, e:
        return jsonify(success=False, exception=str(e))