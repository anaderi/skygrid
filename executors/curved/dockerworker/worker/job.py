import os
import time
import logging
import traceback

import harbor

from ..config import config
from ..log import logger

DELAY_WAIT_DOCKER_MIN = 0.1
DELAY_WAIT_DOCKER_MAX = 10.0


def do_docker_job(job):
    logger.debug("Got job #{} with descriptor: {}".format(job.job_id, job.descriptor))
    try:
        process(job)
        job.update_status("completed")
        logger.debug("Finished job #{}".format(job.job_id))
    except Exception, e:
        job.update_status("failed")
        # job.descriptor['exception'] = str(e) # TODO: add error field to job in metascheduler
        # job.update_descriptor(job.descriptor)

        logger.error(str(e))
        logger.error(traceback.format_exc())
        raise e


def getargs(arg_dict, subst):
    """
    transofrm dict of arguments (kw and positional) to string of arguments,
    and substitute $VARS from subst dict
    """
    args = []
    kw_keys = [k for k in arg_dict.keys() if k.startswith('-')]
    for k in kw_keys:
        v = arg_dict[k]
        if v is True:  # TODO: take care of False value or not?
            args.append(k)
        elif k.startswith('--'):
            args.append("%s=%s" % (k, str(v)))
        else:
            args.append("%s %s" % (k, str(v)))
    pos_keys = sorted([k for k in arg_dict.keys() if k.startswith("__POS")])
    for k in pos_keys:
        v = arg_dict[k]
        if type(v) == str or type(v) == unicode:
            args.append(v)
        else:
            args.extend(v)
    s = ' '.join(args)
    for k, v in subst.iteritems():
        s = s.replace(k, str(v))
    return s


def descriptor_correct(job):
    keys_needed = [
        ('cmd', unicode),
        ('args', dict) ,
        ('cpu_per_container', int),
        ('max_memoryMB', int),
        ('min_memoryMB', int),
        ('env_container', dict)
    ]

    for key, keytype in keys_needed:
        assert isinstance(job.descriptor.get(key), keytype)


def build_command(job):
    args = getargs(job.descriptor['args'],
        {
            "$DATA_DIR": "/data",
            "$OUTPUT_DIR": "/output",
            "$INPUT_DIR": "/input",
            "$JOB_ID": job.job_id,
            "$TIMEHASH": hash(time.time())
        }
    )

    command = "\"{cmd} {args}\"".format(cmd=job.descriptor['cmd'], args=args)

    return command


def create_containers(job, in_dir, out_dir):
    needed = job.descriptor['env_container'].get('needed_containers') or []

    logger.debug("Creating containers for job #{}".format(job.job_id))

    mounted_names = []
    for i, container in enumerate(needed):
        image, volumes = container['name'], container['volumes']
        assert isinstance(volumes, list)

        harbor.pull_image(image)

        tag = "JOB-{}-CNT-{}".format(job.job_id, i)
        mounted_names.append(tag)

        harbor.run(
            image,
            volumes=volumes,
            detach=True,
            name=tag,
            command="echo {} app".format(tag)
        )

    volumes = [
        "{}:/input".format(in_dir),
        "{}:/output".format(out_dir),
    ]
    command = build_command(job)

    logger.debug('Executing: {}'.format(command))

    return harbor.run(
        job.descriptor['env_container']['name'],
        working_dir=job.descriptor['env_container']['workdir'],
        command=command,
        volumes_from=mounted_names,
        volumes=volumes,
        detach=True
    )


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
        logger.debug("job #{}: Fake download input {}".format(job.job_id, input_file))


def upload_output_files(job, out_dir):
    for output_file in os.listdir(out_dir):
        logger.debug("job #{}: Fake upload file `{}`".format(job.job_id, output_file))


def write_std_output(container_id, out_dir):
    with open(os.path.join(out_dir, "stdout"), "w") as stdout_f:
        for logline in harbor.logs(container_id, stdout=True, stderr=False, stream=True):
            stdout_f.write(logline)

    with open(os.path.join(out_dir, "stderr"), "w") as stderr_f:
        for logline in harbor.logs(container_id, stdout=False, stderr=True, stream=True):
            stderr_f.write(logline)



def process(job):
    descriptor_correct(job)

    job_dir, in_dir, out_dir = create_workdir(job)

    get_input_files(job, in_dir)
    container_id = create_containers(job, in_dir, out_dir)

    while harbor.is_running(container_id):
        logger.debug("Container is running. Sleeping for {} sec.".format(config.SLEEP_TIME))
        time.sleep(config.SLEEP_TIME)

    write_std_output(container_id, out_dir)

    upload_output_files(job, out_dir)
