sphinx-autopages
================

    A sphinx extension to generate dynamically pages and counterpart ToC.

.. note::

    Idea taken from `Sphinx Extension Page Generation <https://github.com/Sam-Martin/sphinx-write-pages-tutorial>`_.

Usage
-----

Simply install and add ``sphinx-autopages`` to your ``conf.py`` extensions list.

.. code-block:: bash

    pip install sphinx-autopages



Guide
-----

The most basic usage is to render Toc with the list of page generated.

.. code-block:: rst

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
