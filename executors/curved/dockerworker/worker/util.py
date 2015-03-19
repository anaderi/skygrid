import time

def getargs(arg_dict, subst):
    """
    transofrm dict of arguments (kw and positional) to string of arguments,
    and substitute $VARS from subst dict
   """
    if not arg_dict:
        return ""

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


def descriptor_correct(job):
    keys_needed = [
        ('cmd', unicode),
        ('cpu_per_container', int),
        ('max_memoryMB', int),
        ('min_memoryMB', int),
        ('env_container', dict)
    ]

    for key, keytype in keys_needed:
        assert isinstance(job.descriptor.get(key), keytype)
