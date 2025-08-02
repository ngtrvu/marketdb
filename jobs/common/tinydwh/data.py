import decimal


def sub_dict(keys: list, dict_obj: dict):
    """
    Extract a subset of a dictionary by keys
    :param keys: list of keys to extract
    :param dict_obj: dictionary object
    :return: a new dictionary containing only the specified keys
    """
    results = {}
    for k in keys:
        if k in dict_obj:
            results[k] = dict_obj[k]
    return results


def intersection(list1: list, list2: list):
    """
    Find the intersection of two lists
    :param list1: first list
    :param list2: second list
    :return: a list containing the intersection of the two lists
    """
    return [value for value in list1 if value in list2]


def isNaN(num):
    return num != num


def is_nan(num):
    return num != num


def ensure_number(num, default=None):
    return num if not is_nan(num) else default
