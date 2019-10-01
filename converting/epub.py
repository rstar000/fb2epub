from collections import deque, namedtuple
from uuid import uuid4
from ebooklib import epub
from converting.converters import to_plain_text, to_html
from parsing.book import get_flat_sections

def _author_to_str(author):
    result = ''
    if author.first_name:
        result += author.first_name + ' '

    if author.last_name:
        result += author.last_name

    return result


Node = namedtuple('Node', 'value parent children')

def _read_file(filename):
    with open(filename) as f:
        text = f.read()

    return text


def _node_to_toc(node):
    if node.children:
        return [
            node.value,
            [
                _node_to_toc(child)
                for child in node.children
            ]
        ]
    else:
        return node.value


def _title_to_plain_text(title):
    title_str = to_plain_text(title, line_breaks=False)
    title_str = title_str.replace('\n', ' ')
    return title_str


def make_toc(flat_sections, epub_chapters):
    """
    Convert flat chapters into a tree structure (EPUB table of contents)

    Args:
        flat_sections (list):
            List of parsing.book.FlatSection
        epub_chapters (list):
            List of epub.EpubHtml
    """
    prev_depth = -1
    toc_branches = deque()
    root = Node(epub.Section('Book'), None, [])
    branch = root

    for flat_sec, chapter in zip(flat_sections, epub_chapters):
        depth = flat_sec.depth
        title = _title_to_plain_text(flat_sec.section.header.title)
        is_leaf = len(flat_sec.section.subsections) == 0

        if is_leaf:
            value = chapter
        else:
            value = epub.Section(title)

        new_branch = Node(value, None, [])

        if depth > prev_depth:
            new_branch = new_branch._replace(parent=branch)
            branch.children.append(new_branch)
        elif depth == prev_depth:
            new_branch = new_branch._replace(parent=branch.parent)
            branch.parent.children.append(new_branch)
        else:
            branch = branch.parent
            new_branch = new_branch._replace(parent=branch.parent)
            branch.parent.children.append(new_branch)

        branch = new_branch
        prev_depth = depth

    toc = _node_to_toc(root)
    return toc[1]


def book_to_epub(book, epub_filename):
    epub_book = epub.EpubBook()

    epub_book.set_identifier(str(uuid4()))
    epub_book.set_title(book.description.title)
    epub_book.set_language('en')

    for author in book.description.authors:
        author_str = _author_to_str(author)
        if author_str:
            epub_book.add_author(author_str)

    flat_sections = get_flat_sections(book)
    epub_chapters = []
    for i, flat_section in enumerate(flat_sections):
        section = flat_section.section
        title = _title_to_plain_text(section.header.title)
        epub_chapter = epub.EpubHtml(
            title=title,
            file_name='chapter_{}.xhtml'.format(i),
            lang='ru')

        epub_chapter.add_link(
            href='stylesheet.css',
            rel='stylesheet',
            type='text/css')

        title_html = to_html(section.header.title)
        section_html = to_html(section.contents)
        html = title_html + section_html

        epub_chapter.content = html.encode('utf-8')
        epub_book.add_item(epub_chapter)
        epub_chapters.append(epub_chapter)

    stylesheet_file = 'templates/stylesheet.css'
    css = _read_file(stylesheet_file)
    nav_css = epub.EpubItem(
        uid="css",
        file_name="stylesheet.css",
        media_type="text/css",
        content=css
    )

    # add CSS file
    epub_book.toc = make_toc(flat_sections, epub_chapters)
    epub_book.add_item(epub.EpubNcx())
    # epub_book.add_item(epub.EpubNav())
    epub_book.add_item(nav_css)
    epub_book.spine = epub_chapters
    epub.write_epub(epub_filename, epub_book, {})
    return epub_book
