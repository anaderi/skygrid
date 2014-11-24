import os
import requests

class SkygridServerError(Exception): pass

class u(str):
    """
        Class to deal with urls concat.
    """
    def __init__(self, url):
        self.url = str(url)

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
    json = result.json()

    if json['success']:
        return json['data']
    else:
        raise SkygridServerError(json['exception'])


def sg_post(*args, **kwargs):
    return check_result(requests.post(*args, **kwargs))


def sg_get(*args, **kwargs):
    return check_result(requests.get(*args, **kwargs))


def sg_delete(*args, **kwargs):
    return check_result(requests.delete(*args, **kwargs))


def sg_put(*args, **kwargs):
    return check_result(requests.put(*args, **kwargs))
