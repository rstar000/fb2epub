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
    def __init__(self):
        super().__init__()
        self.text = ''

    def handle(self, token, closing=False):
        if token.type == TokenType.Word:
            self.text += (token.attributes['text'] + ' ')
        elif token.type == TokenType.Paragraph:
            if closing:
                self.text += '\n'
            else:
                self.text += '\t'


def parse_as_plain_text(tokens):
    parser = PlainTextParser()
    for t in tokens:
        parser.add(t)

    return parser.text
