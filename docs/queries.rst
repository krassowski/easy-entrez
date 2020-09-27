**********************
Queries
**********************

:mod:`easy_entrez.queries` defines the supported queries as subclasses of :class:`EntrezQuery`. You should not use this module directly, unless implementing support to a custom endpoint.
The query objects created from :py:class:`EntrezQuery` sub-classes can be executed with :py:meth:`easy_entrez.api.EntrezAPI._request`
(which is not a part of public API, because the preferred way of using the existing queries is by calling the appropriate methods of :py:class:`~easy_entrez.api.EntrezAPI`).

.. currentmodule:: easy_entrez.queries

.. automodule:: easy_entrez.queries
