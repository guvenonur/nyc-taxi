import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def set_logger(name):
    """
    :param str name: logger name
    :return: logger
    :rtype: logger object
    """
    return logging.getLogger(name)
