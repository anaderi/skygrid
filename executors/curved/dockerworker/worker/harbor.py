import os
import re

import docker
from docker import Client

from lockfile import LockFile

from ..log import logger
from ..config import config



client = Client(base_url=config.DOCKER_URL, version=config.DOCKER_API_VERSION)


def pull_image(image, *args, **kwargs):
    with LockFile("/tmp/pull_lock_%s" % re.sub("[:/]", "_", image)):
        logger.debug("Pulling image {}".format(image))
        client.pull(image, *args, **kwargs)



def is_running(containter_id):
    running_ids = [c['Id'] for c in client.containers()]
    return containter_id in running_ids



def run(image, **kwargs):
    logger.debug("Creating container for image {} with arguments: {}".format(image, kwargs))

    volumes_from = None
    if 'volumes_from' in kwargs:
        volumes_from = kwargs['volumes_from']
        del kwargs['volumes_from']

    c = client.create_container(
        image,
        **kwargs
    )

    client.start(c['Id'], volumes_from=volumes_from)

    logger.debug("Created and started container with image={} id={}".format(image, c['Id']))
    return c['Id']


def logs(container_id, **kwargs):
    return client.logs(container_id, **kwargs)
