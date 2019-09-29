from collections import deque
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


def _generate_tokens(elem):
    nodes_queue = deque([elem])
    tail = []

    while nodes_queue:
        node = nodes_queue.pop()
        token = fb2_node_to_token(node)
        if token:
            yield token

        yield from tokenize_text(node.text)

        tail.extend(reversed(list(tokenize_text(node.tail))))
        if needs_closing_token(token):
            tail.append(make_closing())

        nodes_queue.extend(reversed(list(node)))

    yield from reversed(tail)
