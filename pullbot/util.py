import logging


def get_log_level(verbosity):
    """

    :param verbosity:
    :return:
    """
    return max(logging.ERROR - verbosity*10, 0)