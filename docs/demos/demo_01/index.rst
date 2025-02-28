Demo 01
#######

Single page with only one directive ``autopages``.

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

.. autopages:: autopages_callable "arg1" "arg2" debug=True nb_pages=4
   :caption: Demo 01
