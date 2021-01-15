import argparse


def is_empty(text):
    """
    Check string is empty or not

    :param str text: the input string object
    :return: true if string is empty, false otherwise
    :rtype: bool
    """
    return True if text is None or len(str(text).strip()) == 0 else False


def cast_as(value, to=int):
    """
    Check if value is none or not

    :param value: Value to check if none
    :param to: Type to cast
    :return: value or None
    """
    return to(value) if value is not None else value


def parse_args():
    """
    Parse arguments

    :return: dict of params
    :rtype: dict
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--year', help='year of taxi data', required=False, type=str, default='2019')
    parser.add_argument('--month', help='month of taxi data', required=False, type=str, default='01')
    parser.add_argument('--create_table', help='create_table if not created before', required=False, default=False)

    # _: config.ini file
    args, _ = parser.parse_known_args()
    return args.__dict__
