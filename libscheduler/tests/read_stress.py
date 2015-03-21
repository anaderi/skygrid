import time


MS_URL = "http://metascheduler.dev.vs.os.yandex.net/"

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print '%r (%r, %r) %2.2f sec' % \
              (method.__name__, args, kw, te-ts)
        return result
    return timed



from libscheduler import Metascheduler
from multiprocessing import Pool

def read(x):
    print "Start ", x

    ms = Metascheduler(MS_URL)
    q = ms.queue('stress_queue')

    job = q.get()
    while job:
        try:
            job = q.get()
        except:
            print "err", x
            continue



@timeit
def prepare(n):
    ms = Metascheduler(MS_URL)

    q = ms.queue('stress_queue')
    assert q._delete_queue()
    q = ms.queue('stress_queue')

    q.put({
        'descriptor': {"a": "b"},
        'multiply': n
    })


@timeit
def readout():
    p = Pool(4)
    p.map(read, [1,2,3])


if __name__ == "__main__":
    for _ in xrange(3):
        prepare(5000)
        readout()
