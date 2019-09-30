from collections import deque, namedtuple
from enum import Enum

from parsing.utils import maybe
from parsing.rich_text import TokenType as tt
from parsing.rich_text import (
    make_image,
    make_closing,
    make_title,
    make_link,
    make_empty,
    needs_closing_token,
    tokenize_text
)

from .common import fb2_remove_prefix, fb2_get_link_href
from .images import fb2_get_image_id

TAG_TO_TOKEN = {
    'p': tt.Paragraph,
    'strong': tt.Strong,
    'emphasis': tt.Emphasis,
    'style': tt.Style,
    'epigraph': tt.Epigraph,
    'a': tt.Link,
    'code': tt.Code,
    'image': tt.Image,
    'strikethrough': tt.Strikethrough,
    'empty-line': tt.EmptyLine,
    'title': tt.Title,
    'subtitle': tt.Title,
    'cite': tt.Cite
}


@maybe(lambda: [])
def fb2_tokenize(elem):
    return list(_generate_tokens(elem))


def fb2_get_token_type(node):
    tag = fb2_remove_prefix(node.tag)
    token_type = TAG_TO_TOKEN.get(tag)
    if token_type is None:
        print('Unknown tag:', tag)
    return token_type


def _get_title_size(node):
    tag = fb2_remove_prefix(node.tag)
    if tag == 'title':
        return 1
    else:
        return 2


def fb2_node_to_token(node):
    token_type = fb2_get_token_type(node)

    if token_type is None:
        return None

    handlers = {
        tt.Image: lambda x: make_image(fb2_get_image_id(x)),
        tt.Link: lambda x: make_link(fb2_get_link_href(x)),
        tt.Title: lambda x: make_title(_get_title_size(node))
    }

    handler = handlers.get(token_type, lambda x: make_empty(token_type))
    return handler(node)


MarkedNode = namedtuple('MarkedNode', ['value', 'mark'])


def _generate_tokens(elem):
    stack = deque([MarkedNode(elem, False)])

    while stack:
        node = stack.pop()
        token = fb2_node_to_token(node.value)
        element = node.value
        # Unmarked: Traverse the node
        if not node.mark:
            # Add the opening token if necessary
            if token:
                yield token

            yield from tokenize_text(element.text)

            stack.append(node._replace(mark=True))
            children = reversed(list(element))
            stack.extend(map(lambda x: MarkedNode(x, False), children))
        else:  # Marked: Remove node
            yield from tokenize_text(element.tail)
            if needs_closing_token(token):
                yield make_closing()
