import os
import shutil

import util
import harbor

from backend import copy_from_backend, copy_to_backend, list_uploaded

from ..config import config
from ..log import logger


def create_workdir(job):
    job_workdir = os.path.join(config.WORK_DIR, job.job_id)
    os.mkdir(job_workdir)

    input_dir  = os.path.join(job_workdir, "input")
    os.mkdir(input_dir)

    output_dir = os.path.join(job_workdir, "output")
    os.mkdir(output_dir)

    return job_workdir, input_dir, output_dir


def get_input_files(job, in_dir):
    for input_file in job.input:
        logger.debug("Download input {}".format(input_file))
        copy_from_backend(input_file, in_dir)


def create_containers(job, in_dir, out_dir):
    # Add needed containers
    needed = job.descriptor['env_container'].get('needed_containers') or []

    logger.debug("Creating containers")

    mounted_ids = []
    mounted_names = []
    for i, container in enumerate(needed):
        image, volumes = container['name'], container['volumes']
        assert isinstance(volumes, list)

        if not config.ONLY_LOCAL_IMAGES:
            harbor.pull_image(image)

        tag = "JOB-{}-CNT-{}".format(job.job_id, i)
        mounted_names.append(tag)

        c_id = harbor.run(
            image,
            volumes=volumes,
            detach=True,
            name=tag,
        )
        mounted_ids.append(c_id)

    # Execute environment container
    if not config.ONLY_LOCAL_IMAGES:
        harbor.pull_image(job.descriptor['env_container']['name'])

    volumes = [
        "{}:/input".format(in_dir),
        "{}:/output".format(out_dir),
    ]
    command = util.build_command(job)

    logger.debug('Executing: {}'.format(command))

    main_id = harbor.run(
        job.descriptor['env_container']['name'],
        do_start=True,
        working_dir=job.descriptor['env_container']['workdir'],
        command=command,
        volumes_from=mounted_names,
        volumes=volumes,
        detach=True,
        binds={
           in_dir:{'bind': '/input', 'ro': True},
           out_dir:{'bind': '/output', 'ro': False},
        }
    )
    return mounted_ids, main_id


def write_std_output(container_id, out_dir):
    with open(os.path.join(out_dir, "stdout"), "w") as stdout_f:
        for logline in harbor.logs(container_id, stdout=True, stderr=False, stream=True):
            stdout_f.write(logline)

    with open(os.path.join(out_dir, "stderr"), "w") as stderr_f:
        for logline in harbor.logs(container_id, stdout=False, stderr=True, stream=True):
            stderr_f.write(logline)


def upload_output_files(job, out_dir):
    upload_uri = job.descriptor.get('output_uri') # should contain $JOB_ID
    upload_uri = upload_uri.replace('$JOB_ID', job.job_id)

    logger.debug("Upload output directory `{}` to `{}`".format(out_dir, upload_uri))
    copy_to_backend(out_dir, upload_uri)

    job.update_output(list_uploaded(upload_uri))


def pre_remove_hook():
    logger.debug("Executing pre-remove hook: `{}`".format(config.PRE_REMOVE_HOOK))
    os.system(config.PRE_REMOVE_HOOK)


def cleanup(job_dir, cnt_ids):
    logger.debug("Cleaning up")
    for container_id in cnt_ids:
        harbor.remove(container_id, v=True)

    pre_remove_hook()
    shutil.rmtree(job_dir)
