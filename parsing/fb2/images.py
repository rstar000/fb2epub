import base64

from parsing.utils import bytes_to_image, maybe
from typing import NamedTuple

from .common import XLINK
from .common import fb2_find_all


class FB2Binary(NamedTuple):
    id: str
    data: bytes
    content_type: str


def fb2_get_images(root):
    binaries = _parse_binaries(root)
    images = _binaries_to_images(binaries)
    return images


@maybe(None)
def fb2_get_image_id(node):
    return node.attrib['{}href'.format(XLINK)]


def _parse_binaries(root):
    found_binaries = fb2_find_all(root, 'binary')
    binaries = [
        FB2Binary(
            id=binary.attrib['id'],
            data=base64.b64decode(binary.text),
            content_type=binary.attrib['content-type']
        )
        for binary in found_binaries
    ]

    return binaries


def _binaries_to_images(binaries):
    """
    Convert FB2 Binary to a PIL Image if possible
    Args:
        binary (fb2.Binary):
            The binary you want to convert

    Returns:
        PIL.Image, optional - The Image
    """
    formats = {'image/jpeg', 'image/png'}

    images = {
        binary.id: bytes_to_image(binary.data)
        for binary in binaries
        if binary.content_type in formats
    }

    return images
