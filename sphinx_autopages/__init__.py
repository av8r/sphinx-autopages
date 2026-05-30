from typing import Any

from pkg_resources import DistributionNotFound, get_distribution
from sphinx.application import Sphinx

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    __version__ = None


def setup(app: Sphinx) -> dict[str, Any]:
    from sphinx_autopages.sphinx_autopages import (
        AutoPagesDirective,
        on_builder_finished,
        on_builder_inited,
    )

    # https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx.application.Sphinx.add_config_value
    app.add_config_value("autopages_excludes", [], "env")
    app.add_config_value("autopages_cleanup", True, "env")
    app.add_directive("autopages", AutoPagesDirective)
    app.connect("builder-inited", on_builder_inited)
    app.connect("build-finished", on_builder_finished)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
