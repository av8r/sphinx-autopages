sphinx-autopages
================

    A sphinx extension to generate dynamically pages and counterpart ToC.

.. note::

    Idea taken from `Sphinx Extension Page Generation <https://github.com/Sam-Martin/sphinx-write-pages-tutorial>`__.

Usage
-----

Simply install and add ``sphinx_autopages`` to your ``conf.py`` extensions list.

.. code-block:: bash

    pip install sphinx-autopages

.. code-block:: python

   from pathlib import Path

   from sphinx.application import Sphinx
   from sphinx.util import logging

   from sphinx_autopages import __version__

   logger = logging.getLogger(__name__)

    extensions = [
        ...
        'sphinx_autopages',
        ...
    ]


   # -- autopages callable helper
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
       return genfiles




Guide
-----

The most basic usage is to render Toc with the list of page generated.

.. code-block:: RST
   :caption: demo.rst

    Demo
    ----

    .. autopages:: autopages_callable "arg1" "arg2" debug=True nb_pages=4
       :caption: autopages demo



Directive Arguments
-------------------

The first argument, **mandatory**, is the name of the callable helper as found in `conf.py` followed by any optional args and kwargs passed to the callable helper.


Directive Options
-----------------

The autopages directives have the same option as `toctree` directive:

* maxdepth
* name
* class
* caption
* glob
* hidden
* includehidden
* numbered
* titlesonly
* reversed

Configuration
-------------

The following global configuration variables are available:

* None

Callable Helper
---------------

TODO
