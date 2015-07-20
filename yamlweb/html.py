'''
    yamlweb - html

    Converts html-like yaml to html.

    todo:

    @copyright: 2015 by Mike Miller <mgmiller@studioxps>
    @license: GNU GPL 3+
'''
import os
import logging

from . import basestring

log = logging.getLogger(__name__)
META_STD_ATTRS = ('charset', 'content', 'http-equiv', 'name', 'scheme')


def check_encoding_tag(root, encoding):
    ''' Adds a meta tag specifiying character encoding if necessary.
        # <meta charset="utf-8" /> '''
    from xml.etree.cElementTree import Element
    head = root.find('head')
    found = False
    for meta in head.findall('meta'):
        if 'charset' in meta.attrib:
            found = True
        elif ('http-equiv' in meta.attrib) and ('content' in meta.attrib):
            if 'charset' in meta.get('content', ''):
                found = True

    if not found:
        head.insert(0, Element('meta', dict(charset=encoding)))


def convert_to_html(data, indent=False, encoding=None):
    ''' Convert elementtree to html. '''
    from xml.etree.cElementTree import tostring
    from .utils import tree_indent  # defer

    root = walk_dict(data)
    if encoding:
        check_encoding_tag(root, encoding)

    if indent:
        tree_indent(root, width=indent)

    return tostring(root, method='html', encoding=encoding)


def parse_key(key):
    ''' Parse the various components of yaml keys into tag and html attrs. '''
    from .utils import shplit
    tag, _, attrs = key.partition(' ')  # at first space

    # short cuts
    if '#' in tag:
        tag, _, id_ = key.partition('#')
        attrs += ' id=' + id_

    if '.' in tag:
        tag, _, class_ = key.partition('.')
        attrs += ' class=' + class_

    if not tag:
        tag = 'div'

    log.debug('attrs: %r', attrs)
    attrs = [ attr.partition('=')[::2] for attr in shplit(attrs) ]
    # fix boolean attrs  :/
    attrs = sorted([ (attr[0], attr[1] or attr[0]) for attr in attrs ])

    return tag, attrs


def walk_dict(dictionary, base=None):
    ''' Walk the tree, handle various cases.  Should be broken up. '''
    from xml.etree.cElementTree import Element, SubElement  # defer

    log.debug('base: %s', base)
    for key, val in dictionary.iteritems():
        log.debug('%s %s', key, val)
        tag, attrs = parse_key(key)

        if tag == 'meta':
            newattrs = []
            for name, content in attrs:
                if name not in META_STD_ATTRS:
                    newattrs.append(('name', name))
                    newattrs.append(('content', content))
            attrs = newattrs
        elif tag == 'style':
            log.debug('val %s, type %s', val, type(val))
            val = convert_to_css(val, indent=4) # indent?

        if (base is None):
            log.debug('creating root %s', tag)
            if tag == 'html':
                base = Element(tag)
                [ base.set(*attr)  for attr in attrs ]
                walk_dict(val, base=base)
            else:
                base = Element('html')
                log.debug('creating child %s', tag)
                child = SubElement(base, tag)
                [ child.set(*attr)  for attr in attrs ]
                walk_dict(val, base=child)
            continue

        if isinstance(val, dict):
            log.debug('creating child %s', tag)
            child = SubElement(base, tag)
            [ child.set(*attr)  for attr in attrs ]
            walk_dict(val, base=child)

        elif isinstance(val, list):
            log.debug('creating children %s', tag)
            child = SubElement(base, tag)
            [ child.set(*attr)  for attr in attrs ]
            for item in val:
                log.debug('list item: %s', item)
                if isinstance(item, basestring):
                    if list(child):  # has children, put next string behind
                        gchild = list(child)[-1]
                        log.debug('looking at gchild, %s', gchild.tag)
                        gchild.tail = (gchild.tail or '') + item + '\n'
                    else:
                        child.text = (child.text or '') + item + '\n'
                elif isinstance(item, dict):
                    walk_dict(item, base=child)
        else:
            log.debug('creating child %s', tag)
            child = SubElement(base, tag)
            [ child.set(*attr)  for attr in attrs ]
            child.text = val if val else ''

    return base


def main(args):
    # defer loading modules to improve --help response time
    from pprint import pformat
    import yaml
    from .utils import SafeOrdLoader, get_output_filename
    from .css import convert_to_css
    global convert_to_css  # :/ defer loading

    status = os.EX_OK
    for infile in args.infile:
        log.info('reading "%s"', infile.name)
        with infile:
            data = yaml.load(infile, SafeOrdLoader)
            log.debug(pformat(data))

        html = convert_to_html(data, indent=args.indent,
                               encoding=args.encoding)

        outfile = ( open(get_output_filename(infile), 'wb')
                    if args.to_html else args.output )
        log.info('writing "%s"', outfile.name)
        with outfile:
            if args.doctype:
                outfile.write((args.doctype + '\n').encode(args.encoding)) #py3
            outfile.write(html)

    log.info('done.')
    return status
