#-*- coding:utf-8 -*-
'''
    yamlweb - utils

    Bag of tools.

    @copyright: 2015 by Mike Miller <mgmiller@studioxps>
    @license: GNU GPL 3+
'''
import sys, os
import logging
import yaml

log = logging.getLogger(__name__)

# figure correct function to import, though used elsewhere
try:
    from ushlex import split as shplit
except ImportError:
    from shlex import split as shplit
    if sys.version < '3.0':
        log.warning('Warning: shlex module cannot handle unicode. '
                    'install ushlex.')
shplit  # make pyflakes happy


class MultiMap(dict):
    ''' Holds an ordered list of pairs while masquerading as a dictionary.
        Keeps order like the OrderedDict, but also duplicate keys,
        which is useful to represent HMTL nodes.
    '''
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return repr(self.value)

    def iteritems(self):
        for pair in self.value:
            yield pair


class SafeOrdLoader(yaml.BaseLoader):
    ''' An ordered and simplified/safe yaml loader.

        Disables the use of "%" chars as directive characters,
        and {}, [] as inline flow characters so we can use templating
        languages and don't have to quote so much. Also @ & etc.
    '''
    #~ def check_directive(self):
        #~ return False

    def check_plain(self):
        ch = self.peek()
        return ch not in u'\0 \t\r\n\x85\u2028\u2029-?:!|>\'\"`' \
                or (self.peek(1) not in u'\0 \t\r\n\x85\u2028\u2029'
                    and (ch == u'-' or (not self.flow_level and ch in u'?:')))
        return True

    def fetch_more_tokens(self):
        'Override this to skip several chars like %, {, and }.'
        from yaml.scanner import ScannerError

        # Eat whitespaces and comments until we reach the next token.
        self.scan_to_next_token()

        # Remove obsolete possible simple keys.
        self.stale_possible_simple_keys()

        # Compare the current indentation and column. It may add some tokens
        # and decrease the current indentation level.
        self.unwind_indent(self.column)

        # Peek the next character.
        ch = self.peek()

        # Is it the end of stream?
        if ch == u'\0':
            return self.fetch_stream_end()

        # Is it a directive?
        #~ if ch == u'%' and self.check_directive():
            #~ return self.fetch_directive()

        # Is it the document start?
        if ch == u'-' and self.check_document_start():
            return self.fetch_document_start()

        # Is it the document end?
        if ch == u'.' and self.check_document_end():
            return self.fetch_document_end()

        # TODO: support for BOM within a stream.
        #if ch == u'\uFEFF':
        #    return self.fetch_bom()    <-- issue BOMToken

        # Note: the order of the following checks is NOT significant.

        #~ # Is it the flow sequence start indicator?
        #~ if ch == u'[':
            #~ return self.fetch_flow_sequence_start()

        #~ # Is it the flow mapping start indicator?
        #~ if ch == u'{':
            #~ return self.fetch_flow_mapping_start()

        #~ # Is it the flow sequence end indicator?
        #~ if ch == u']':
            #~ return self.fetch_flow_sequence_end()

        #~ # Is it the flow mapping end indicator?
        #~ if ch == u'}':
            #~ return self.fetch_flow_mapping_end()

        #~ # Is it the flow entry indicator?
        #~ if ch == u',':
            #~ return self.fetch_flow_entry()

        # Is it the block entry indicator?
        if ch == u'-' and self.check_block_entry():
            return self.fetch_block_entry()

        # Is it the key indicator?
        if ch == u'?' and self.check_key():
            return self.fetch_key()

        # Is it the value indicator?
        if ch == u':' and self.check_value():
            return self.fetch_value()

        # Is it an alias?
        #~ if ch == u'*':
            #~ return self.fetch_alias()

        # Is it an anchor?
        #~ if ch == u'&':
            #~ return self.fetch_anchor()

        # Is it a tag?
        if ch == u'!':
            return self.fetch_tag()

        # Is it a literal scalar?
        if ch == u'|' and not self.flow_level:
            return self.fetch_literal()

        # Is it a folded scalar?
        if ch == u'>' and not self.flow_level:
            return self.fetch_folded()

        # Is it a single quoted scalar?
        if ch == u'\'':
            return self.fetch_single()

        # Is it a double quoted scalar?
        if ch == u'\"':
            return self.fetch_double()

        # It must be a plain scalar then.
        if self.check_plain():
            return self.fetch_plain()

        # No? It's an error. Let's produce a nice error message.
        raise ScannerError('while scanning for the next token', None,
                'found character %r that cannot start any token'
                % ch.encode('utf-8'), self.get_mark())

    def _construct_mapping(loader, node):
        ''' Keep duplicates and order in mappings,
            uses a list of (name, val) tuple pairs instead.
        '''
        return MultiMap(loader.construct_pairs(node))

# register it
SafeOrdLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                              SafeOrdLoader._construct_mapping)


def get_output_filename(infile, ext='.html'):
    ''' Change extension of given filename. '''
    basename, _ = os.path.splitext(infile.name)
    return basename + ext


def tree_indent(elem, level=0, width=4):
    ''' Poor-man's pretty html printer
        http://effbot.org/zone/element-lib.htm#prettyprint
    '''
    spaces = width * ' '
    indent = '\n' + (level * spaces)
    if len(elem):
        if elem.text:
            elem.text = elem.text.rstrip() + indent + spaces
        if not elem.text or not elem.text.strip():
            elem.text = indent + spaces  # one level extra

        if elem.tail:
            elem.tail = elem.tail.rstrip() + indent
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent

        for elem in elem:
            tree_indent(elem, level+1)

        if not elem.tail or not elem.tail.strip():
            elem.tail = indent
    else:
        if elem.tail:
            elem.tail = elem.tail.rstrip() + indent
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent
