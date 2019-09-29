from xml.etree import ElementTree
from parsing.book import Book

from .section import fb2_parse_section
from .description import fb2_parse_description
from .common import fb2_find, fb2_find_all
from .images import fb2_get_images

__all__ = ['read_fb2']


def read_fb2(filename):
    with open(filename, 'rb') as fb2_file:
        tree = ElementTree.parse(fb2_file)

    fb2_root = tree.getroot()

    # Description
    fb2_desc = fb2_find(fb2_root, 'description')
    title_info = fb2_find(fb2_desc, 'title-info')
    description = fb2_parse_description(title_info)

    # Body
    fb2_body = fb2_find(fb2_root, 'body')
    sections = list(map(fb2_parse_section, fb2_find_all(fb2_body, 'section')))
    # Binaries
    images = fb2_get_images(fb2_root)

    return Book(
        description=description,
        meta_info=None,
        sections=sections,
        images=images
    )
