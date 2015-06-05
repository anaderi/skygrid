from time import sleep
from multiprocessing import Process

from .api import Metascheduler
from .common import MetaschedulerServerError

class WorkerMS(object):
    """
    Class to run job_func on jobs from MS in parallel
    """
    def __init__(self, api_url, queue_name, job_func, threads_num=2, sleep_time=10):
        self.ms = Metascheduler(api_url)
        self.queue = self.ms.queue(queue_name)
        self.sleep_time = sleep_time
        self.do_job = job_func

        self.cpu_avail = threads_num
        self.cpus_per_job = {} # job_id -> needed_cpus
        self.processes = []

        self.running = False


    def start(self):
        self.running = True
        self.run()

    def stop(self):
        self.running = False
        for p in self.processes:
            p.terminate()

    def fail_all(self):
        self.cleanup_processes()
        self.stop()
        processes_snapshot = self.processes[:]
        for p in processes_snapshot:
            job_id = p.name.strip("job:")
            job = self.ms.job(job_id)
            job.update_status('failed')

    def sleep(self):
        sleep(self.sleep_time)


    def cleanup_processes(self):
        processes_snapshot = self.processes[:]
        for p in processes_snapshot:
            if not p.is_alive():
                self.processes.remove(p)
                self.release_cpus(p.name)


    def acquire_cpus(self, process_name, ncpus):
        self.cpus_per_job[process_name] = ncpus
        self.cpu_avail -= ncpus


    def release_cpus(self, process_name):
        self.cpu_avail += self.cpus_per_job[process_name]
        self.cpus_per_job.pop(process_name, None)
        print "Released cpu, available: ", self.cpu_avail


    def run(self):
        while self.running:
            self.cleanup_processes()

            if self.cpu_avail <= 0:
                self.sleep()
                continue

            try:
                job = self.queue.get(cpu_available=self.cpu_avail)
            except MetaschedulerServerError:
                job = None

            if not job:
                self.sleep()
                continue

            process_name = 'job:{}'.format(job.job_id)

            self.acquire_cpus(
                process_name,
                job.descriptor.get('cpu_per_container') or 1
            )

            p = Process(name=process_name, target=self.do_job, args=(job,))
            self.processes.append(p)
            p.start()
