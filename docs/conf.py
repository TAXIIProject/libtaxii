import libtaxii

project = u'libtaxii'
copyright = u'2014, The MITRE Corporation'
version = libtaxii.__version__
release = version

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.ifconfig',
    'sphinx.ext.intersphinx',
    'sphinxcontrib.napoleon',
]

intersphinx_mapping = {
    'python': ('http://docs.python.org/', None),
}

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

rst_prolog = """
.. warning::

    This documentation is still a work in progress. If you have any issues or
    questions, please ask on the taxii-discussion mailing list or file a bug
    in our `issue tracker`_.

.. _issue tracker: https://github.com/TAXIIProject/libtaxii/issues
"""

exclude_patterns = ['_build']
pygments_style = 'sphinx'

html_theme = 'default'
html_style = '/default.css'
html_static_path = ['_static']
htmlhelp_basename = 'libtaxiidoc'

html_theme_options = {
    'codebgcolor': '#EEE',
    'footerbgcolor': '#FFF',
    'footertextcolor': '#000',
    'headbgcolor': '#CCC',
    'headtextcolor': '#000',
    'headlinkcolor': '#ED8603',
    'linkcolor': '#666',
    'relbarbgcolor': '#EDB603',
    'relbarlinkcolor': '#000',
    'relbartextcolor': '#FFF',
    'sidebarbgcolor': '#EEE',
    'sidebarlinkcolor': '#666',
    'sidebartextcolor': '#000',
    'visitedlinkcolor': '#666',
}

latex_elements = {}
latex_documents = [
  ('index', 'libtaxii.tex', u'libtaxii Documentation',
   u'The MITRE Corporation', 'manual'),
]


def skip_non_api_items(app, what, name, obj, skip, options):
    if name in ['BaseNonMessage',
                'get_message_from_httplib_http_response',
                'get_message_from_urllib2_httperror',
                'get_message_from_urllib_addinfourl',
                'HTTPClientAuthHandler',
                'HTTPSClientAuthHandler']:
        return True
    return False

def setup(app):
    app.connect('autodoc-skip-member', skip_non_api_items)
