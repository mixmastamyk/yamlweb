#~ # -*- coding: utf-8 -*-
#~ from os.path import join
from distutils.core import setup

from yamlweb import __version__, __progname as name


# readme is needed at register/upload time, not install time
try:
    with open('readme.rst') as f:
        long_description = f.read()
except IOError:
    long_description = ''


setup(
    name              = name,
    version           = __version__,
    description       = 'Converts YAML to HTML and CSS.',
    author            = 'Mike Miller',
    author_email      = 'mixmastamyk@github.com',
    url               = 'https://github.com/mixmastamyk/%s' % name,
    download_url      = ('https://github.com/mixmastamyk/%s/archive/master.zip'
                         % name),
    license           = 'GPLv3+',
    requires          = ['PyYAML(>=3.10,<4.0)', ], #+ requires, # for pypi page
    install_requires  = ['PyYAML>=3.10,<4.0a0', ], #+ requires,  # real reqs

    packages          = [name],
    scripts           = ['yaml2html', 'yaml2css'],
    #~ package_data      = {name: ['', '']},

    #~ extras_require = {
        #~ 'win': ['colorama', 'fcrypt'],
    #~ },

    long_description  = long_description,
    classifiers       = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
)
