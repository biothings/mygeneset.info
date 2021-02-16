Quick start
-----------

`MyGeneset.info <http://mygeneset.info>`_ provides two simple web services: one for querying stored geneset objects and the other for geneset annotation retrieval. Both return results in `JSON <http://json.org>`_ format.

Geneset query service
^^^^^^^^^^^^^^^^^^^^^


URL
"""""
::

    http://mygeneset.info/v1/query

Examples
""""""""
::

    # Search genesets with 'glucose' in a default query field (geneset name or description)
    http://mygeneset.info/v1/query?q=glucose

    # Retreive NCBI gene ids for genes in genesets with 'glucose' in a default query field
    http://mygeneset.info/v1/query?q=glucose&fields=genes.ncbigene

    # Fetch all genesets containing the gene with symbol ABL1
    http://mygeneset.info/v1/query?q=genes.symbol:ABL1

    # Filter the previous query to human species
    http://mygeneset.info/v1/query?q=genes.symbol:ABL1&species=human

    # Fetch all genesets belonging to two mice or human organisms
    http://mygeneset.info/v1/query?species=mouse,human

    # Fetch all genesets from the source "wikipathways"
    http://mygeneset.info/v1/query?q=_exists_:wikipathways

    # Wildcard queries
    http://mygeneset.info/v1/query?q=genes.symbol=cdk?
    http://mygeneset.info/v1/query?q=genes.symbol=IL*

    # Search genesets containing all of the provided genes
    http://localhost:8000/v1/query?q=genes.symbol:(ABL1 AND CEBPA AND FLT3)&fields=all

    # Search genesets containing any of the provided genes
    http://localhost:8000/v1/query?q=genes.symbol:(ABL1 OR CEBPA OR FLT3)&fields=all


.. Hint:: View nicely formatted JSON results in your browser with this handy add-on: `JSON formater <https://chrome.google.com/webstore/detail/bcjindcccaagfpapjjmafapmmgkkhgoa>`_ for Chrome or `JSONView <https://addons.mozilla.org/en-US/firefox/addon/jsonview/>`_ for Firefox.



To learn more
"""""""""""""

* You can read `the full description of our query syntax here <doc/query_service.html>`__.
* Try it live on `interactive API page <http://mygeneset.info/v1/api/>`__.
* Batch queries? Yes, you can. do it with `a POST request <doc/query_service.html#batch-queries-via-post>`_.



Geneset annotation service
^^^^^^^^^^^^^^^^^^^^^^^^^^

URL
"""""
::

    http://mygeneset.info/v1/geneset/<genesetid>

Examples
""""""""
::

    http://mygeneset.info/v1/geneset/WP100
    http://mygeneset.info/v1/geneset/GO_0000002_9606
    http://mygeneset.info/v1/geneset/R-HSA-112043?fields=genes.ensemblgene,reactome,taxid


To learn more
"""""""""""""

* You can read `the full description of our query syntax here <doc/annotation_service.html>`__.
* Try it live on `interactive API page <http://mygeneset.info/v1/api>`_.
* Yes, batch queries via `POST request <doc/annotation_service.html#batch-queries-via-post>`_ as well.
