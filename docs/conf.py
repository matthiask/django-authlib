from __future__ import unicode_literals

import os
import sys

sys.path.append(os.path.abspath('..'))

extensions = []

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = 'django-authlib'
copyright = '2016 - 2017 Feinheit AG'

version = __import__('authlib').__version__
release = version

pygments_style = 'sphinx'

html_theme = 'alabaster'

html_static_path = ['_static']

htmlhelp_basename = 'djangoauthlibdoc'

latex_documents = [(
    'index',
    'djangoauthlib.tex',
    'django-authlib Documentation',
    'Feinheit AG',
    'manual',
)]

man_pages = [(
    'index',
    'djangoauthlib',
    'django-authlib Documentation',
    ['Feinheit AG'],
    1,
)]

texinfo_documents = [(
    'index',
    'djangoauthlib',
    'django-authlib Documentation',
    'Feinheit AG',
    'djangoauthlib',
    'Authentication utilities for Django',
    'Miscellaneous',
)]
