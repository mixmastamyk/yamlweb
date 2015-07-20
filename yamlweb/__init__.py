
__version__ = '0.50'


# python 3 support
try:
    basestring = basestring
except NameError:
    basestring = str

basestring  # make pyflakes happy
