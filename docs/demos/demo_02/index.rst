Demo 02
#######

Single page with multiple directives ``autopages``.

conf.py
-------

Add in your conf.py:

.. literalinclude:: ../callables/autopages.py
   :language: python

page.rst
--------

.. literalinclude:: ./index.rst
   :language: rst


Output:
.......

.. autopages:: autopages_callable debug=False nb_pages=2
   :caption: Demo 02 1/2


.. autopages:: autopages_callable debug=False nb_pages=2
   :caption: Demo 02 2/2