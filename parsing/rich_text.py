from enum import Enum
from collections import namedtuple, deque
from typing import List

from parsing.utils import maybe


TokenType = Enum('TokenType', [
    'Word',   # text: str
    'Strong',
    'Emphasis',
    'Style',
    'Cite',
    'Epigraph',
    'Strikethrough',
    'Paragraph',
    'Link',   # href: str
    'Image',  # id: str
    'Code',
    'Title',  # size: int
    'Closing',
    'EmptyLine'
])

Token = namedtuple('Token', ['type', 'attributes'])
RichText = List[Token]

NON_CLOSING_TOKENS = {
    TokenType.Word,
    TokenType.Image,
    TokenType.EmptyLine
}


def make_empty(token_type):
    return Token(token_type, {})


def make_token(token_type, attrs):
    return Token(token_type, attrs)


def make_link(href):
    return make_token(TokenType.Link, {'href': href})


def make_title(size):
    assert size > 0 and size <= 5
    return make_token(TokenType.Title, {'size': size})


def make_image(image_id):
    return make_token(TokenType.Image, {'id': image_id})


def make_closing():
    return make_empty(TokenType.Closing)


def make_word(text):
    return make_token(TokenType.Word, {'text': text})


@maybe(lambda: False)
def needs_closing_token(token):
    return token.type not in NON_CLOSING_TOKENS


@maybe(lambda: [])
def tokenize_text(text):
    return [make_word(text)]
    # words = text.split()
    # return map(make_word, words)


class BaseParser:
    def __init__(self):
        self._tokens = deque()

    def add(self, token):
        if token.type == TokenType.Closing:
            closed = self._tokens.pop()
            self.handle(closed, closing=True)
        else:
            if needs_closing_token(token):
                self._tokens.append(token)

            self.handle(token)

    def handle(self, token, closing=False):
        raise NotImplementedError()


class PlainTextParser(BaseParser):
    def __init__(self, line_breaks=True):
        super().__init__()
        self.text = ''
        self._line_breaks = line_breaks

    def handle(self, token, closing=False):
        if token.type == TokenType.Word:
            self.text += (token.attributes['text'] + ' ')
        elif token.type == TokenType.Paragraph:
            if closing and self._line_breaks:
                self.text += '\n'


def _link_to_html(token, closing):
    if closing:
        return '</a>'
    else:
        return '<a href={}>'.format(token.attributes['href'])


class HTMLParser(BaseParser):
    TOKEN_TO_TAG = {
        TokenType.Strong: ('<span class="b">', '</span>'),
        TokenType.Emphasis: ('<span class="i">', '</span>'),
        TokenType.Style: ('<span class="u">', '</span>'),
        TokenType.Cite: ('<cite>', '</cite>'),
        TokenType.Epigraph: ('<span class="epigraph">', '</span>'),
        TokenType.Paragraph: ('<p>', '</p>'),
        TokenType.Code: ('<span class="monospace>', '</span>'),
        TokenType.Title: ('<div class="heading">', '</div>'),
        TokenType.EmptyLine: ('<br>', ''),
    }

    TOKEN_HANDLERS = {
        TokenType.Link: _link_to_html
    }

    def __init__(self):
        super().__init__()
        self.text = ''

    def handle(self, token, closing=False):
        if token.type == TokenType.Word:
            self.text += (token.attributes['text'] + ' ')
        elif token.type in self.TOKEN_TO_TAG:
            open_tag, close_tag = self.TOKEN_TO_TAG[token.type]
            if closing:
                self.text += close_tag
            else:
                self.text += open_tag
        elif token.type in self.TOKEN_HANDLERS:
            handler = self.TOKEN_HANDLERS[token.type]
            self.text += handler(token, closing)


def parse_as_plain_text(tokens, line_breaks=True):
    parser = PlainTextParser(line_breaks=line_breaks)
    for t in tokens:
        parser.add(t)

    return parser.text


def parse_as_html(tokens):
    parser = HTMLParser()
    for t in tokens:
        parser.add(t)

    return parser.text
