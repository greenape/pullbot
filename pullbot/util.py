import logging


def get_log_level(verbosity):
    """

    :param verbosity:
    :return:
    """
    return logging.ERROR - verbosity*10