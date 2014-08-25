import json

import requests


payload = {
    "name": "test_task", # generates automatically if not given from user/env/script fields
    "environments": ["anaderi/ocean"],
    "owner": "anaderi",
    "app": "my_app_container",
    "email": "andrey@none.com",
    "workdir": "/opt/ship/build",
    "cmd": "/opt/ship/python/muonShieldOptimization/g4ex.py",
    "args": {
        "default": ["--runNumber=1", "--nEvents=123", "--ecut=1"],
        "scaleArg": [   # arguments used by job scheduler for job splitting/parallelization
            ["nEvents", "SCALE", 1000], # how large is the whole job
            ["ecut", "SET", [1, 10, 100]], # the whole number of events should be split equally among differnt values of SET, RANGE params
            ["rcut", "RANGE", [1, 100]], # the whole number of events should be split equally among differnt values of SET, RANGE params
            ["runNumber", "RANDOM_SEED"], # random seed argument, that should be different for each sub task
        ]
    },
    "num_containers": 10, # recommendation for number of parallel workers
    "min_memoryMB": 512,
    "max_memoryMB": 1024,
    "cpu_per_container": 1,
}


r = requests.post("http://test02cern.vs.os.yandex.net:5000/add_job", data=json.dumps(payload))

print r.text
