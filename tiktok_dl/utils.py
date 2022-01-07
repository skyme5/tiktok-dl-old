import re
from datetime import datetime

from loguru import logger
from requests.exceptions import InvalidURL


def format_utctime(time: int, fmt: str):
    return datetime.utcfromtimestamp(time).strftime(fmt)


def search_regex(
    pattern, string: str, name: str, default=object(), fatal=True, flags=0, group=None
):
    """
    Perform a regex search on the given string, using a single or a list of
    patterns returning the first matching group.
    In case of failure return a default value or raise a WARNING or a
    RegexNotFoundError, depending on fatal, specifying the field name.
    """
    if isinstance(pattern, (str, type(re.compile("")))):
        mobj = re.search(pattern, string, flags)
    else:
        for p in pattern:
            mobj = re.search(p, string, flags)
            if mobj:
                break

    if mobj:
        if group is None:
            # return the first matching group
            return next(g for g in mobj.groups() if g is not None)
        else:
            return mobj.group(group)
    elif default is not default:
        return default
    elif fatal:
        raise re.error("Unable to extract %s" % name)
    else:
        logger.error("unable to extract {}", name)
        return None


def valid_url_re():
    return re.compile(
        r"https?://www\.tiktokv?\.com/(?:@[\w\._]+|share)/video/(?P<id>\d+)"
    )


def match_id(url: str, valid_re):
    m = valid_re.match(url)
    if m is None:
        raise InvalidURL("Url is invalid {}".format(url))
    if m.group("id") is None:
        raise re.error("unable to find video id {}".format(url))

    return str(m.group("id"))


def try_get(src, getter, expected_type=None):
    if not isinstance(getter, (list, tuple)):
        getter = [getter]
    for get in getter:
        try:
            v = get(src)
        except (AttributeError, KeyError, TypeError, IndexError):
            pass
        else:
            if expected_type is None or isinstance(v, expected_type):
                return v


def str_or_none(v, default=None):
    return default if v is None else str(v)


def int_or_none(v, scale=1, default=None, get_attr=None, invscale=1):
    if get_attr:
        if v is not None:
            v = getattr(v, get_attr, None)
    if v == "":
        v = None
    if v is None:
        return default
    try:
        return int(v) * invscale // scale
    except (ValueError, TypeError):
        return default
