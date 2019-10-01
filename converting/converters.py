from collections import deque
from parsing.rich_text import TokenType as tt
from parsing.rich_text import needs_closing_token


class BaseConverter:
    def __init__(self):
        self._tokens = deque()

    def add(self, token):
        if token.type == tt.Closing:
            closed = self._tokens.pop()
            self.handle(closed, closing=True)
        else:
            if needs_closing_token(token):
                self._tokens.append(token)

            self.handle(token)

    def handle(self, token, closing=False):
        raise NotImplementedError()


class PlainTextConverter(BaseConverter):
    def __init__(self, line_breaks=True):
        super().__init__()
        self.text = ''
        self._line_breaks = line_breaks

    def handle(self, token, closing=False):
        if token.type == tt.Word:
            self.text += (token.attributes['text'] + ' ')
        elif token.type == tt.Paragraph:
            if closing and self._line_breaks:
                self.text += '\n'


def _link_to_html(token, closing):
    if closing:
        return '</a>'
    else:
        return '<a href={}>'.format(token.attributes['href'])


class HTMLConverter(BaseConverter):
    TOKEN_TO_TAG = {
        tt.Strong: ('<span class="b">', '</span>'),
        tt.Emphasis: ('<span class="i">', '</span>'),
        tt.Style: ('<span class="u">', '</span>'),
        tt.Cite: ('<cite>', '</cite>'),
        tt.Epigraph: ('<span class="epigraph">', '</span>'),
        tt.Paragraph: ('<p>', '</p>'),
        tt.Code: ('<span class="monospace>', '</span>'),
        tt.Title: ('<div class="heading">', '</div>'),
        tt.EmptyLine: ('<br>', ''),
    }

    TOKEN_HANDLERS = {
        tt.Link: _link_to_html
    }

    def __init__(self):
        super().__init__()
        self.text = ''

    def handle(self, token, closing=False):
        if token.type == tt.Word:
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


def to_plain_text(tokens, line_breaks=True):
    parser = PlainTextConverter(line_breaks=line_breaks)
    for t in tokens:
        parser.add(t)

    return parser.text


def to_html(tokens):
    parser = HTMLConverter()
    for t in tokens:
        parser.add(t)

    return parser.text
