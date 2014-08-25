import datetime
from time import sleep

from ..generic.models import Worker, Job

SLEEP_TIME = 1
WORKER_ROT_TIME = datetime.timedelta(seconds=5)
JOB_ROT_TIME = datetime.timedelta(seconds=2)

def rot_workers():
    """
    Move long sleeping workers to inactive status
    """
    now = datetime.datetime.now()

    workers = Worker.objects(
        last_seen__lte=(now - WORKER_ROT_TIME),
        active=True
    )

    for worker in workers:
        print "<Worker: {}> has rotten!".format(worker)
        worker.active = False
        worker.save()

        for job in Job.objects(assigned_worker=worker):
            job.assigned_worker = None
            job.status = "submitted"
            job.save()


def rot_jobs():
    """
    Set job's assigned worker to null, if worker has not sent any info about it for some SLEEP_TIME
    """
    now = datetime.datetime.now()

    jobs = Job.objects(
        last_update__lte=(now - JOB_ROT_TIME),
        assigned_worker__ne=None,
        status="submitted"
    )

    for job in jobs:
        print "Job has rotten: ", job

        job.assigned_worker = None
        job.save()



def main():
    while True:
        sleep(SLEEP_TIME)

        rot_workers()
        rot_jobs()
    

if __name__ == "__main__":
    main()