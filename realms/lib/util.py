import re
import os
import hashlib
import json

from flask import request
from recaptcha.client import captcha

from realms import config
from realms.lib.services import cache


def cache_it(fn):
    def wrap(*args, **kw):
        key = "%s:%s" % (args[0].table, args[1])
        data = cache.get(key)
        # Assume strings are JSON encoded
        try:
            data = json.loads(data)
        except TypeError:
            pass
        except ValueError:
            pass

        if data is not None:
            return data
        else:
            data = fn(*args)
            print data
            ret = data
            if data is None:
                data = ''
            if not isinstance(data, basestring):
                try:
                    data = json.dumps(data, separators=(',', ':'))
                except TypeError:
                    pass
            cache.set(key, data)
            return ret
    return wrap


def to_json(res, first=False):
    """
    Jsonify query result.
    """
    res = to_dict(res, first)
    return json.dumps(res, separators=(',', ':'))


def to_dict(cur, first=False):
    if not cur:
        return None
    ret = []
    for row in cur:
        ret.append(row)
    if ret and first:
        return ret[0]
    else:
        return ret

def validate_captcha():
    response = captcha.submit(
        request.form['recaptcha_challenge_field'],
        request.form['recaptcha_response_field'],
        config.flask['RECAPTCHA_PRIVATE_KEY'],
        request.remote_addr)
    return response.is_valid


def mkdir_safe(path):
    if path and not(os.path.exists(path)):
        os.makedirs(path)
    return path


def extract_path(file_path):
    if not file_path:
        return None
    last_slash = file_path.rindex("/")
    if last_slash:
        return file_path[0, last_slash]


def clean_path(path):
    if path:
        if path[0] != '/':
            path.insert(0, '/')
        return re.sub(r"//+", '/', path)


def extract_name(file_path):
    if file_path[-1] == "/":
        return None
    return os.path.basename(file_path)


def remove_ext(path):
    return os.path.splitext(path)[0]


def clean_url(url):
    if not url:
        return url

    url = url.replace('%2F', '/')
    url = re.sub(r"^/+", "", url)
    return re.sub(r"//+", '/', url)


def to_canonical(s):
    """
    Double space -> single dash
    Double dash -> single dash
    Remove all non alphanumeric and dash
    Limit to first 64 chars
    """
    s = s.encode('ascii', 'ignore')
    s = str(s)
    s = re.sub(r"\s\s*", "-", s)
    s = re.sub(r"\-\-+", "-", s)
    s = re.sub(r"[^a-zA-Z0-9\-]", "", s)
    s = s[:64]
    return s


def gravatar_url(email):
    return "https://www.gravatar.com/avatar/" + hashlib.md5(email).hexdigest()