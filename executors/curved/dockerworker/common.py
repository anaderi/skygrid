from ..log import logger

from util import sh, test_sh, SUCCESS, ERROR_EXCEPTION

def execute(command, *args, **kwargs):
    logger.debug("Executing: {}".format(command))
    result = sh(command, *args, **kwargs)

    if result['rc'] != SUCCESS:
        raise Exception("Error executing `{}`. result=`{}`, status=`{}`".format(command, result['rc'], result['status']))
    return result