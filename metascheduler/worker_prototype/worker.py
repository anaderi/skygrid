from time import sleep
from libscheduler.queue import QueueMS

class WorkerBase(object):
    def __init__(self, queue_name, sleep_time=5):
        self.queue = QueueMS(queue_name)
        self.sleep_time = sleep_time

    def run(self):
        self.running = True

        while self.running:
            job = self.queue.get()

            if job:
                self.do_impl(job)
            else:
                sleep(self.sleep_time)

    def stop(self):
        self.running = False


    def do_impl(self, job):
        """
        Inherited classes should implement this method.
        """
        pass
 

class MyWorker(WorkerBase):
    def do_impl(self, job):
        print job
# result = job
# result['description']['num'] += 1

def main():
    worker = MyWorker('test_queue')
    worker.run()


if __name__ == '__main__':
    main()