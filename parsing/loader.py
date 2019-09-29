import hashlib

from parsing import fb2
# from parsing import epub

import sys
import hashlib

def compute_hash(filename):
    sha1sum = hashlib.sha1()
    with open(filename, 'rb') as source:
        block = source.read(2**16)
        while len(block) != 0:
            sha1sum.update(block)
            block = source.read(2**16)

    result = sha1sum.hexdigest()
    return result


def load(filename):
    file_hash = compute_hash(filename)
    if filename.endswith('.fb2'):
        return file_hash, fb2.parse(filename)
    else:
        raise RuntimeError("Unable to parse the file")