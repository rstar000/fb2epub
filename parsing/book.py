from collections import deque
from typing import List, NamedTuple, Optional, Dict, Union
from PIL import Image
from parsing.rich_text import RichText

"""
Abstract book parser based on FB2 format
The book consists of Sections that can further contain more Sections
or have Paragraphs of text or other objects (Leaves)

This file contains utilities and basic classes to make
book parsing possible.
"""


MaybeString = Optional[str]


class SectionHeader(NamedTuple):
    title: RichText
    image: Optional[Image.Image]


class Section(NamedTuple):
    header: SectionHeader
    contents: RichText
    subsections: List


class Author(NamedTuple):
    first_name: MaybeString
    last_name: MaybeString
    nickname: MaybeString


class Description(NamedTuple):
    title: str
    authors: List[Author]
    genres: List[str]
    date: str
    cover: Optional[str]
    annotation: Optional[RichText]
    series: List[str]


class MetaInfo(NamedTuple):
    filename: str
    uid: str
    format: str


class Book(NamedTuple):
    description: Description
    meta_info: MetaInfo
    sections: List
    images: Dict[str, Image.Image]


class FlatSection(NamedTuple):
    section: Section
    depth: int


def get_flat_sections(book):
    """
    Flatten the section tree and get a list of flat sections.

    Args:
        book (Book): the parsed book

    Returns:
        list of FlatSection
    """
    traversed = []
    to_traverse = deque(_add_depth(book.sections, 0))

    while to_traverse:
        s, depth = to_traverse.popleft()
        traversed.append((s, depth))
        to_traverse.extendleft(_add_depth(reversed(s.subsections), depth + 1))

    return traversed


def _add_depth(sections, depth):
    return map(lambda x: FlatSection(x, depth), sections)