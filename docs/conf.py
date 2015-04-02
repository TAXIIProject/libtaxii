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
**Version**: {}
""".format(release)

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
html_sidebars = {"**": ['localtoc.html', 'relations.html', 'sourcelink.html',
                        'searchbox.html', 'links.html']}

latex_elements = {}
latex_documents = [
    ('index', 'libtaxii.tex', u'libtaxii Documentation',
     u'The MITRE Corporation', 'manual'),
]
