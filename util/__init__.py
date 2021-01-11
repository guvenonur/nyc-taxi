def is_empty(text):
    """
    Check string is empty or not

    :param str text: the input string object
    :return: true if string is empty, false otherwise
    :rtype: bool
    """
    return True if text is None or len(str(text).strip()) == 0 else False
