import base64
import io

from typing import NamedTuple
from xml.etree import ElementTree as ET
from PIL import Image

import parsing.book as book

from parsing.utils import bytes_to_image
from parsing.rich_text import Token
from parsing.rich_text import TokeType as tt


TAG_TO_TOKEN = {
    'p': tt.Paragraph,
    'strong': tt.Strong,
    'emphasis': tt.Emphasis,
    'style': tt.Style,
    'epigraph': TokeType.Epigraph,
    'a': tt.Link,
    'code': tt.Code,
    'image': tt.Image,
    'strikethrough': tt.Strikethrough
}


def parse(filename):
    with open(filename, 'rb') as fb2_file:
        tree = ET.parse(fb2_file)

    fb2_root = tree.getroot()

    # Description
    fb2_desc = _find(fb2_root, 'description')
    title_info = _find(fb2_desc, 'title-info')
    description = parse_description(title_info)

    # Body
    fb2_body = _find(fb2_root, 'body')

    # Binaries
    binaries = _parse_binaries(fb2_root)
    images = _get_images(binaries)

    return book.Book(
        description=description,
        meta_info=None,
        sections=None,
        images=images
    )


