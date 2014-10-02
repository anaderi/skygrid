import requests

class ServerError(Exception): pass


def check_result(result):
    if result['success']:
        return result
    else:
        raise ServerError(result['exception'])


def ms_post(*args, **kwargs):
    r = requests.post(*args, **kwargs)

    return check_result(r.json())


def ms_get(*args, **kwargs):
    r = requests.get(*args, **kwargs)

    return check_result(r.json())


def ms_delete(*args, **kwargs):
    r = requests.delete(*args, **kwargs)

    return check_result(r.json())


def ms_put(*args, **kwargs):
    r = requests.put(*args, **kwargs)

    return check_result(r.json())
