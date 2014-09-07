import os
import re
import json
import time
import subprocess
import traceback
import shlex
import logging

SUCCESS = 0
ERROR_INTERRUPT = 253
ERROR_EXCEPTION = 254
ERROR_DEAD = 127

logger = logging.getLogger()


def sh(cmd, input=None, verbose=False, logout=None, logerr=None):
    if verbose: logger.info("`%s`" % cmd)
    cmd_args = shlex.split(cmd.encode('ascii'))
    result = {
        'status': "",
        'out': None,
        'err': None,
        'rc': 0
    }
    try:
        fh_out, fh_err = (subprocess.PIPE, subprocess.PIPE)
        if logout is not None:
            fh_out = open(logout, "w")
        if logerr is not None:
            fh_err = open(logerr, "w")
        proc = subprocess.Popen(cmd_args, stdout=fh_out, stderr=fh_err)
        logger.debug("PID: %d" % proc.pid)
        try:
            # result['rc'] = proc.wait()
            # TODO increase delay progressively
            delay = 0.5
            while True:
                rc = proc._internal_poll(_deadstate=ERROR_DEAD)
                if rc is not None:
                    if rc == ERROR_DEAD:
                        rc = SUCCESS  # HACK to avoid ZOmbies
                    result['rc'] = rc
                    break
                else:
                    time.sleep(delay)
        except KeyboardInterrupt:
            print "^C in util (%d)" % proc.pid
            proc.kill()
            result['rc'] = ERROR_INTERRUPT
            result['status'] = "Terminated by ^C"

        if fh_out != subprocess.PIPE:
            fh_out.close()
            with open(logout, "r") as fh_out:
                out = fh_out.read()
        else:
            out = proc.stdout.read()
        if fh_err != subprocess.PIPE:
            fh_err.close()
            with open(logerr, "r") as fh:
                err = fh.read()
        else:
            err = proc.stderr.read()

        if out is not None and len(out) > 0:
            if verbose:
                print "===OUT===\n%s" % out
            if logout is not None:
                with open(logout, "a") as fh:
                    fh.write(out)
        if err is not None and len(err) > 0:
            if verbose:
                print "===ERR===\n%s" % err
            if logerr is not None:
                with open(logerr, "a") as fh:
                    fh.write(err)
        result['out'] = out
        result['err'] = err
    except Exception:
        result['status'] = traceback.format_exc()
        result['rc'] = ERROR_EXCEPTION
    return result


def test_sh():
    result = sh("ls -l", verbose=False)
    assert result['rc'] == 0, result
    filename = result['out'].split("\n")[2].split()[8]
    print "FILENAME:", filename
    result = sh("ls -l", verbose=True)
    assert result['rc'] == 0
    assert filename in result['out']
    result = sh("ls -l", verbose=True, logout="log.log")
    assert result['rc'] == 0
    assert os.path.exists("log.log")
    result = sh("rm log1.log", verbose=True, logerr="err.log")
    assert result['rc'] != 0
    assert os.path.exists("err.log")
    result = sh("rm log.log", verbose=True)
    assert result['rc'] == 0
    result = sh("rm err.log", verbose=True)
    assert result['rc'] == SUCCESS
    result = sh("xxx err.log", verbose=True)
    assert result['rc'] == ERROR_EXCEPTION
    print "ERR:", result['status']
    result = sh("echo 'no split single quotes'", verbose=True)
    assert result["rc"] == 0
    assert result["out"].strip() == "no split single quotes"
    print "OK"


class QueueDir(object):

    def __init__(self, dirname, default_mask="%d_job.json"):
        self.dirname = os.path.abspath(dirname)
        if os.path.exists(dirname):
            assert os.path.isdir(dirname), "%s is not a directory" % dirname
        else:
            os.makedirs(dirname)
        self.mask = self._detect_mask(default_mask)
        logger.debug(self)

    def __str__(self):
        return "QueueDir: %s, mask: %s, count: %d" % (self.dirname, self.mask, self.qsize())

    def _detect_mask(self, default_mask):
        masks = {default_mask: 0}
        for name in os.listdir(self.dirname):
            mgroups = re.match("(\D*)(\d+)(\D*)", name)
            if mgroups is not None:
                mask = "%s%%d%s" % (mgroups.groups()[0], mgroups.groups()[2])
                if mask in masks:
                    masks[mask] += 1
                else:
                    masks[mask] = 1
        sorted_keys = sorted(masks, key=masks.get)
        return sorted_keys[-1]

    def qsize(self):
        return len(self.__unsorted_list_name_id())

    def empty(self):
        return self.qsize() == 0

    def __get_max_id(self):
        name_id = self.__unsorted_list_name_id()
        if len(name_id) == 0:
            return 0
        sorted_name_id = sorted(name_id, key=lambda x: x[1])
        return sorted_name_id[-1][1]

    def __unsorted_list_name_id(self):
        m_re = self.mask.replace("%d", "(\d+)")
        name_id_list = [(name, int(re.match(m_re, name).groups()[0]))
                        for name in os.listdir(self.dirname) 
                        if re.match(m_re, name) is not None]
        return name_id_list

    def list_files(self):
        name_id = self.__unsorted_list_name_id()
        sorted_name_id = sorted(name_id, key=lambda x: x[1])
        return ["%s/%s" % (self.dirname, i[0]) for i in sorted_name_id]

    def __iter__(self):
        return self

    def next(self):
        if self.empty():
            raise StopIteration
        return self.get()

    def clear(self):
        self.get_n(self.qsize())

    def extend(self, iterable):
        for i in iterable:
            self.put(i)

    def put(self, item):
        i = self.__get_max_id() + 1
        filename = os.path.join(self.dirname, self.mask % i)
        logger.debug("put: %s // %s" % (filename, item))
        with open(filename, "w") as fh:
            json.dump(item, fh, indent=2, sort_keys=True)

    def get_n(self, count):
        queue_items_names = self.list_files()
        actual_count = min(count, len(queue_items_names))
        if actual_count == 0:
            return None
        filenames = queue_items_names[0:actual_count]
        result = []
        for filename in filenames:
            with open(filename) as fh:
                item = json.load(fh)
            if item is not None:
                os.remove(filename)
                logger.debug("get: %s" % item)
                result.append(item)
        return result

    def get(self):
        result = self.get_n(1)
        if result is None:
            return None
        else:
            return result[0]


def test_queue():
    import shutil
    dirs = ["_d1", "_d2"]
    for d in dirs:
        if os.path.exists(d):
            shutil.rmtree(d)
    q1 = QueueDir(dirs[0])
    item = q1.get()
    assert item is None
    assert q1.qsize() == 0
    assert q1.empty()
    i1 = {'key': 1}
    q1.put(i1)
    assert q1.qsize() == 1
    o1 = q1.get()
    assert i1 == o1
    assert q1.qsize() == 0
    os.makedirs(dirs[1])
    with open("%s/sub123" % dirs[1], "w") as fh:
        json.dump("123", fh)
    q2 = QueueDir(dirs[1])
    q2.put(i1)
    q2.put({'key': 2})
    assert q2.qsize() == 3
    l = []
    for i in q2:
        logger.info("iter: %s" % i)
        l.append(i)
    assert q2.empty()
    q1.extend(l)
    assert q1.qsize() == 3

    i1 = q1.get()
    q1.put(i1)
    assert q1.qsize() == 3, q1.qsize()
    arr1 = q1.get_n(2)
    assert len(arr1) == 2
    arr1 = q1.get_n(2)
    assert len(arr1) == 1

    with open("%s/sub123" % dirs[1], "w") as fh:
        json.dump("123", fh)
    with open("%s/sub1" % dirs[1], "w") as fh:
        json.dump("1", fh)
    assert q2.qsize() == 2
    assert q2.get() == "1"
    q2.clear()
    assert q2.qsize() == 0
    for d in dirs:
        if os.path.exists(d):
            shutil.rmtree(d)
