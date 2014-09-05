import json
from time import sleep
from multiprocessing import Process

import requests


WORKER_ID = 0
SLEEP_TIME = 1
ALIVE = True

PAYLOAD = {
    "name": "test_job", # generates automatically if not given from user/env/script fields
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
            ["runNumber", "RANDOM_SEED"], # random seed argument, that should be different for each sub job
        ]
    },
    "num_containers": 10, # recommendation for number of parallel workers
    "min_memoryMB": 512,
    "max_memoryMB": 1024,
    "cpu_per_container": 1,
}


def hearbeat():
    global ALIVE
    while ALIVE:
        r = requests.get(
            "http://test02cern.vs.os.yandex.net:5000/beat/" + str(WORKER_ID)
        )
        # print "Beat result:", r.text
        sleep(SLEEP_TIME)


def upload_job():
    "Submit job to master and return its id"
    r = requests.post("http://test02cern.vs.os.yandex.net:5000/add_job", data=json.dumps(PAYLOAD))
    result = r.json()

    assert result['success']

    return result['job']['id']


def get_jobs(jobs):
    r = requests.get("http://test02cern.vs.os.yandex.net:5000/get_jobs?wid={}&njob=2".format(WORKER_ID))
    result = r.json()
    
    assert result['success']

    assert result['jobs'][0]['id'] in jobs
    assert result['jobs'][1]['id'] in jobs



def main():
    # Start beating
    beat_process = Process(target=hearbeat)
    beat_process.start()

    # Submit two job. Update one, assert second is unassigned "submitted state"
    jobs = [upload_job(), upload_job()]

    assert jobs[0] != jobs[1]

    get_jobs(jobs)

    url = "http://test02cern.vs.os.yandex.net:5000/jobs/{}".format(jobs[0])
    print url

    r = requests.post(url, data={'status': 'running'})
    print r.json()

    raw_input()

    print "We good! Now finishing..."
    ALIVE = False
    beat_process.terminate()




if __name__ == '__main__':
    main()