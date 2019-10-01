from itertools import chain
from parsing.book import Section, SectionHeader

from .tokenizer import fb2_tokenize
from .common import fb2_find, fb2_find_all, fb2_remove_prefix
from .images import fb2_get_image_id


# TODO: remove recursion
def fb2_parse_section(node):
    title = []
    image = None
    contents = []

    subsections = fb2_find_all(node, 'section')
    subsections = list(map(fb2_parse_section, subsections))

    children = iter(node)
    child = next(children)

    if fb2_remove_prefix(child.tag) == 'title':
        title = fb2_tokenize(child)
        child = next(children)

    while fb2_remove_prefix(child.tag) == 'epigraph':
        contents.extend(fb2_tokenize(child))
        child = next(children)

    if fb2_remove_prefix(child.tag) == 'image':
        image = fb2_get_image_id(child)
        child = next(children)

    while fb2_remove_prefix(child.tag) == 'annotation':
        contents.append(fb2_tokenize(child))
        child = next(children)

    remaining = [child] + list(children)
    # Tokenize remaining children and flatten the token list
    if not subsections:
        contents.extend(chain.from_iterable(map(fb2_tokenize, remaining)))

    return Section(
        header=SectionHeader(title, image),
        contents=contents,
        subsections=subsections)
