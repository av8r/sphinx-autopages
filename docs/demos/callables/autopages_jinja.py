from pathlib import Path

from lorem_text import lorem
from sphinx.application import Sphinx
from sphinx.util import logging

logger = logging.getLogger(__name__)


def autopages_jinja_callable(app: Sphinx, *args, **kwargs) -> list[str]:  # noqa: ANN002, ANN003
    """
    Demo autopages_callable. generate

    :param app: Sphinx app
    :param args: Any args
    :param kwargs: Any kwargs, from_doc(str) caller page, debug (bool) to enable debug, nb_pages (int) to specify the number of pages
    :return: List of pages (str) generated in current directory
    """
    if kwargs.get("debug", False):
        logger.info(f"autopages_jinja_callable - args: {args}")
        logger.info(f"autopages_jinja_callable - kwargs: {kwargs}")
        logger.info(f"Sphinx extensions: {app.config.extensions}")

    prefix = kwargs.get("prefix", "file")

    genfiles = []
    nb_pages = max(int(kwargs.get("nb_pages", "0")), 1)
    for (file_name, idx) in [(Path(f"{prefix}_{i}"), i) for i in range(nb_pages)]:
        with open(f"{file_name}.rst", "w") as f:
            from_doc = kwargs.get("from_doc")
            title = f"Test ({from_doc}) - {file_name}" if from_doc else f"Test - {file_name}"
            f.write(f"{title}\n{'=' * len(title)}")
            f.write(f"""


..jinja::
  :ctx: {{"name": "{kwargs.get("from_doc", "")}"}}

    Welcome
    Build from {{{{name}}}}!

    .. autopages:: autopages_callable debug=True nb_pages=4
       :caption: Build by Jinja ({idx}/{nb_pages})

""")

        genfiles.append(str(file_name))
    return genfiles
