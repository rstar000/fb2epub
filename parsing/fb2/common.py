from xml.etree import ElementTree
from parsing.utils import remove_prefix

fb2_ns = 'http://www.gribuser.ru/xml/fictionbook/2.0'
XLINK = '{http://www.w3.org/1999/xlink}'
fb2 = '{' + fb2_ns + '}'

ns = {'fb2': fb2_ns}


def fb2_find(node, tag):
    return node.find('fb2:{tag}'.format(tag=tag), ns)


def fb2_find_all(node, tag):
    return node.findall('fb2:{tag}'.format(tag=tag), ns)


def fb2_get_text(node, tag):
    found = fb2_find(node, tag)
    if found is None:
        return None

    return found.text


def fb2_remove_prefix(tag):
    return remove_prefix(tag, fb2)


def fb2_get_link_href(node):
    return node.attrib['{}href'.format(XLINK)]
