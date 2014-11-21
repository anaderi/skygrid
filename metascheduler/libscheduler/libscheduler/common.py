import os
import requests

class MetaschedulerServerError(Exception): pass

class u(object):
    def __init__(self, url):
        self.url = url

    def __add__(self, other):
        if isinstance(other, u):
            return u(os.path.join(self.url, other.url))
        else:
            return u(os.path.join(self.url, other))

    def __unicode__(self):
        return self.url

    def __repr__(self):
        return self.url


def check_result(result):
    result.raise_for_status()
    result = result.json()

    if result['success']:
        return result
    else:
        raise MetaschedulerServerError(result['exception'])


def ms_post(*args, **kwargs):
    r = requests.post(*args, **kwargs)

    return check_result(r)


def ms_get(*args, **kwargs):
    r = requests.get(*args, **kwargs)

    return check_result(r)


def ms_delete(*args, **kwargs):
    r = requests.delete(*args, **kwargs)

    return check_result(r)


def ms_put(*args, **kwargs):
    r = requests.put(*args, **kwargs)

    return check_result(r)
