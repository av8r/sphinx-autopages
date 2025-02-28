Demo 03
#######

Recursive directives ``autopages`` via `sphinx-jinja2 <https://sphinx-jinja2.readthedocs.io/>`_.

conf.py
-------

Add in your conf.py:

.. literalinclude:: ../callables/autopages.py
   :language: python

.. literalinclude:: ../callables/autopages_jinja.py
   :language: python

output:
-------

.. autopages:: autopages_callable debug=False nb_pages=2 prefix="page"
   :caption: Generated Pages


.. autopages:: autopages_jinja_callable debug=False nb_pages=4 prefix="page_jinja"
   :caption: Jinja Pages
