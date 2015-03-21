from libscheduler.queue import QueueMS
from multiprocessing import Pool

def f(x):
    q = QueueMS('test_queue', api_url="http://test02cern.vs.os.yandex.net:5000/")
    for i in xrange(1000):
        q.put({"value": i})
        if i % 100 == 0:
            print "%d: written %d!" % (x, i)


p = Pool(4)
p.map(f, [1,2,3,4,5])
