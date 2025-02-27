from pathlib import Path

from sphinx.application import Sphinx
from sphinx.util import logging

logger = logging.getLogger(__name__)

try:
    from sphinx_autopages import __version__
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    sys.setrecursionlimit(1500)
    from sphinx_autopages import __version__



project = "sphinx-autopages"
copyright = "Stephane ENGEL"  # noqa: A001
version = __version__ or "DEV"

extensions = [
    "sphinx_autopages",
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


def autopages_callable(app: Sphinx, *args, **kwargs) -> list[str]:  # noqa: ANN002, ANN003
    """
    Demo autopages_callable. generate

    :param app: Sphinx app
    :param args: Any args
    :param kwargs: Any kwargs, from_doc(str) caller page, debug (bool) to enable debug, nb_pages (int) to specify the number of pages
    :return: List of pages (str) generated in current directory
    """
    logger.info(f"autopage_callable - args: {args}")
    logger.info(f"autopage_callable - kwargs: {kwargs}")

    genfiles = []
    nb_pages = min(int(kwargs.get("nb_pages", 0)), 1)
    for file_name in [Path(f"file_{i}") for i in range(1, nb_pages)]:
        with open(f"{file_name}.rst", "w") as f:
            if kwargs.get("debug", False):
                logger.warning(f.name)
            from_doc = kwargs.get("from_doc")
            title = f"Test({from_doc}) - {file_name}" if from_doc else f"Test - {file_name}"
            f.write(f"{title}\n{'=' * len(title)}")
            genfiles.append(str(file_name))
    logger.warning(genfiles)
    return genfiles
