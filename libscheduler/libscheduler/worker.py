from time import sleep
from multiprocessing import Process

from .api import Metascheduler

class WorkerMS(object):
    """
    Class to run job_func on jobs from MS in parallel
    """
    def __init__(self, api_url, queue_name, job_func, threads_num=2, sleep_time=10):
        self.ms = Metascheduler(api_url)
        self.queue = self.ms.queue(queue_name)
        self.sleep_time = sleep_time
        self.do_job = job_func

        self.threads_num = threads_num
        self.processes = []

        self.running = False


    def start(self):
        self.running = True
        self.run()

    def stop(self):
        self.running = False
        for p in self.processes:
            p.terminate()


    def sleep(self):
        sleep(self.sleep_time)


    def cleanup_processes(self):
        processes_snapshot = self.processes[:]
        for p in processes_snapshot:
            if not p.is_alive():
                self.processes.remove(p)


    def run(self):
        while self.running:
            self.cleanup_processes()

            if not len(self.processes) < self.threads_num:
                self.sleep()
                continue

            try:
                job = self.queue.get()
            except:
                job = None

            if not job:
                self.sleep()
                continue

            p = Process(name='job:{}'.format(job.job_id), target=self.do_job, args=(job,))
            self.processes.append(p)
            p.start()
