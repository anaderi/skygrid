import os
import re

import docker
from docker import Client

from common import execute
from ..log import logger


client = Client(base_url='unix://var/run/docker.sock', version="1.16")


def pull_image(image, *args, **kwargs):
    with LockFile("/tmp/jeeves_lock_pull_%s" % re.sub("[:/]", "_", image)):
        logger.debug("Pulling image {}".format(image))
        client.pull(image, *args, **kwargs)


def is_running(container):
    tempfile = "/tmp/jeeves.%d" % os.getpid()

    ret = None

    try:
        ret = bool(client.inspect_container(container))
    except docker.errors.APIError:
        ret = False

    os.remove(tempfile)

    return ret


def is_container_running(containerID):
    result = False
    check_result = sh("sudo docker ps", verbose=False)
    assert len(check_result['err']) == 0, "got error while 'docker ps': %s" % check_result['err']
    assert check_result['rc'] == 0, "got non-zero result while 'docker ps'"
    result = containerID[:12] in check_result['out']
    return result


def run(image, **kwargs):
    c = client.create_container(
        image,
        **kwargs
    )

    c.start(c['Id'])
    return c['Id']
