import sys
from pathlib import Path

from sphinx.util import logging

logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.setrecursionlimit(1500)
from demos import autopages_callable  # noqa: E402

try:
    from sphinx_autopages import __version__
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    sys.setrecursionlimit(1500)
    from sphinx_autopages import __version__



project = "sphinx-autopages"
copyright = "Stephane ENGEL"  # noqa: A001
version = __version__ or "DEV"

extensions = [
    "sphinx_autopages",
    "autodoc2",
    "sphinx.ext.viewcode",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
]

# autodoc2
if "autodoc2" in extensions:
    autodoc2_packages = [
        {
            "path": "../sphinx_autopages",
        },
    ]
    autodoc2_hidden_objects = ["dunder", "private", "inherited"]
    autodoc2_replace_annotations = [
        ("re.Pattern", "typing.Pattern"),
        ("markdown_it.MarkdownIt", "markdown_it.main.MarkdownIt"),
    ]
    autodoc2_replace_bases = [
        ("sphinx.directives.SphinxDirective", "sphinx.util.docutils.SphinxDirective"),
    ]
    autodoc2_docstring_parser_regexes = [
        # ("myst_parser", "myst"),
        # (r"myst_parser\.setup", "myst"),
    ]
    nitpicky = True
    nitpick_ignore_regex = [
        (r"py:.*", r"docutils\..*"),
        (r"py:.*", r"sphinx\..*"),
    ]
    nitpick_ignore = [
        # ("py:obj", "myst_parser._docs._ConfigBase"),
        # ("py:exc", "MarkupError"),
        # ("py:class", "sphinx.util.typing.Inventory"),
        # ("py:class", "sphinx.writers.html.HTMLTranslator"),
        # ("py:obj", "sphinx.transforms.post_transforms.ReferencesResolver"),
    ]

# -- theme setup
html_theme = "pydata_sphinx_theme"
html_title = "sphinx-autopages"
# html_favicon = "_static/favicon.svg"
html_static_path = ["_static"]
# html_css_files = ["custom.css"]
html_show_sourcelink = True
# https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/version-dropdown.html
html_theme_options = {
    "navbar_center": ["version-switcher", "navbar-nav"],
    # "check_switcher": False,
    # "switcher": {
    #     "version_match": "main_doc",
    #     # "json_url": "http://127.0.0.1:8080/json_switcher.js",
    #     "json_url": "/json_switcher.js",
    #     # "check_switcher": False,
    # },
    "show_toc_level": 2,
    "use_edit_page_button": False,
    # "external_links": [
    #     {
    #         "name": "Redocly",
    #         "url": "/redoc",
    #         "icon": "fa-brands fa-dochub",
    #         "type": "fontawesome",
    #     },
    # ],
    # "icon_links": [
    #     {
    #         "name": "Swagger",
    #         "url": "/docs",
    #         "icon": "fa-brands fa-codepen",
    #         "type": "fontawesome",
    #     },
    #     {
    #         "name": "Admin",
    #         "url": "/admin",
    #         "icon": "fa-solid fa-user-tie",
    #         "type": "fontawesome",
    #     },
    #     # "primary_sidebar_end": ["indices", "slidebar-ethical-ads.html"]
    # ],
}

# Ensure callable
for helper_callable in [
    autopages_callable
]:
    if not callable(helper_callable):
        raise RuntimeError(f"{helper_callable} is not callable")
