import io

from functools import wraps
from PIL import Image


def remove_prefix(s, p):
    if not s.startswith(p):
        return s

    return s[len(p):]


def bytes_to_image(data):
    try:
        img = Image.open(io.BytesIO(data))
    except IOError:
        return None

    return img


def maybe(nothing=None):
    if nothing is None:
        nothing = lambda: None

    def decorate(f):
        @wraps(f)
        def wrapper(x):
            if x is None:
                return nothing()
            return f(x)

        return wrapper
    return decorate
