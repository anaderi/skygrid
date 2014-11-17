import os
import json
import click

from libscheduler import Metascheduler

API_URL = os.environ.get('MSCLI_API_URL')
if not API_URL:
    raise Exception('MSCLI_API_URL environment variable should be set!')

ms = Metascheduler(API_URL)

@click.group()
def cli():
    pass

@cli.command()
@click.argument('queue_name')
@click.option('--job-json', type=str)
@click.option('--job-file', type=click.File('r'))
def submit(queue_name, job_json, job_file):
    queue = ms.queue(queue_name)
    
    if job_json:
        job_dict = json.loads(job_json)
    elif job_file:
        job_dict = json.loads(job_file.read())
    else:
        raise click.UsageError('Job should be specified either by json or from file.')

    queue.put(job_dict)


@cli.command()
@click.argument('queue_name')
def pull(queue_name):
    queue = ms.queue(queue_name)
    job = queue.get()
    if not job:
        return

    click.echo(job.json())
