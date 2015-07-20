'''
    yamlweb - css

    Converts css-like yaml to css.

    todo:

    @copyright: 2015 by Mike Miller <mgmiller@studioxps>
    @license: GNU GPL 3+
'''
import os
import logging
import re

from . import basestring

log = logging.getLogger(__name__)
hex_color_finder = re.compile(r'\b([0-9A-F]{3}|[0-9A-F]{6})\b', re.IGNORECASE)
log_isEnabledFor, log_level_DEBUG = log.isEnabledFor, logging.DEBUG # shortcuts


def check_for_colors(value):
    ''' Prepends a hash/pound symbol to hex colors per css rules. '''
    result = re.sub(hex_color_finder, r'#\1', value)
    if log_isEnabledFor(log_level_DEBUG):  # speed up frequent checks
        if value != result:
            log.debug('value %r was updated to %r.', value, result)
    return result


def convert_to_css(data, indent=0):
    ''' Convert dict to css. '''
    indent = ' ' * indent
    nwln = '\n' if indent else ''
    space = ' ' if indent else ''
    csstext = ''

    for key, val in data.iteritems():
        log.debug('%s %s', key, val)
        if isinstance(val, dict):
            csstext += '%s%s%s{%s' % (nwln, key, space, nwln)
            for chkey, chval in val.iteritems():
                log.debug('%s %s', chkey, chval)

                if isinstance(chval, dict):  # media directive, etc.
                    for gkey, gval in chval.iteritems():
                        gkey, gval = handle_pair(gkey, gval)
                        csstext += '%s%s%s{%s' % (indent, chkey, space, nwln)
                        csstext += '%s%s:%s%s;%s' % (indent*2, gkey, space, gval, nwln)
                        csstext += '%s}%s' % (indent, nwln)
                else:
                    chkey, chval = handle_pair(chkey, chval)
                    csstext += '%s%s:%s%s;%s' % (indent, chkey, space, chval, nwln)
            csstext += '}' + nwln
        else:
            log.error('bogus value found here: %r %r', key, val)

    return csstext


def handle_pair(key, val):

    if key.startswith('bg'):  # shortcut
        key = key.replace('bg', 'background', 1) # only once

    elif key == 'content':
        val = "'%s'" % val
        log.debug('quoting content: %s', val)

    if isinstance(val, basestring):  # temporary?
        val = check_for_colors(val)

    return key, val


def main(args):
    # defer loading modules to improve --help response time
    from pprint import pformat
    import yaml
    from .utils import SafeOrdLoader, get_output_filename

    status = os.EX_OK
    for infile in args.infile:
        log.info('reading "%s"', infile.name)
        with infile:
            try:
                data = yaml.load(infile, SafeOrdLoader)
                log.debug(pformat(data))
            except yaml.YAMLError as err:
                log.critical('unable to continue: %s', err)
                return os.EX_DATAERR

        csstext = convert_to_css(data, indent=args.indent)
        try:
            outfile = ( open(get_output_filename(infile, ext='.css'), 'wb')
                        if args.to_css else args.output )
            log.info('writing "%s"', outfile.name)
            with outfile:
                if args.encoding:
                    outfile.write(('@charset: "%s";\n' %
                                  args.encoding).encode(args.encoding)) # py3
                    csstext = csstext.encode(args.encoding)
                outfile.write(csstext)
        except IOError as err:
            log.critical('unable to write file: %s', err)
            return os.EX_CANTCREAT

    log.info('done.')
    return status

