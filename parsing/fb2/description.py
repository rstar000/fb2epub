from parsing.book import Description, Author
from .common import fb2_find_all, fb2_find, fb2_get_text
from .images import fb2_get_image_id
from .tokenizer import fb2_tokenize


def fb2_parse_description(title_info):
    """
    Parses the fb2 <description> tag.
    Returns book.Description
    """
    return Description(
        title=_parse_title(title_info),
        authors=_parse_authors(title_info),
        genres=_parse_genres(title_info),
        annotation=_parse_annotation(title_info),
        date=_parse_date(title_info),
        series=_parse_series(title_info),
        cover=_parse_cover(title_info)
    )


def _parse_title(title_info):
    return fb2_get_text(title_info, 'book-title')


def _parse_author(author):
    """
    Parses FB2 <author> tag.
    Args:
        author (etree.Element)

    Returns:
        book.Author
    """
    return Author(
        first_name=fb2_get_text(author, 'first-name'),
        last_name=fb2_get_text(author, 'last-name'),
        nickname=fb2_get_text(author, 'nickname'),
    )


def _parse_authors(title_info):
    authors = fb2_find_all(title_info, 'author')
    authors = [_parse_author(author) for author in authors]
    return authors


def _parse_genres(title_info):
    genres = fb2_find_all(title_info, 'genre')
    genres = [g.text for g in genres]
    return genres


def _parse_annotation(title_info):
    annotation = fb2_find(title_info, 'annotation')
    return fb2_tokenize(annotation)


def _parse_date(title_info):
    date = fb2_get_text(title_info, 'date')
    return date


def _parse_series(title_info):
    series = fb2_find_all(title_info, 'series')
    return [s.attrib['name'] for s in series]


def _parse_cover(title_info):
    cover = fb2_find(title_info, 'coverpage')
    if cover is None:
        return None
    else:
        return fb2_get_image_id(fb2_find(cover, 'image'))
