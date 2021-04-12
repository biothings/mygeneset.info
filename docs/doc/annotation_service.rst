Geneset annotation service
**************************

This page describes the reference for MyGeneset.info geneset annotation web service. It's also recommended to try it live on our `interactive API page <http://mygeneset.info/v1/api>`_.

Service endpoint
=================
::

    http://mygeneset.info/v1/geneset

GET request
==================

To obtain the geneset annotation via our web service is as simple as calling this URL::

    http://mygeneset.info/v1/geneset/<genesetid>

By default, this will return the complete geneset annotation object in JSON format. See `here <#returned-object>`_ for an example and :ref:`here <gene_object>` for more details. If the input **genesetid** is not valid, 404 (NOT FOUND) will be returned.

Optionally, you can pass a "**fields**" parameter to return only the annotations you want (by filtering returned object fields)::

    http://mygeneset.info/v1/geneset/WP100?fields=genes.ncbigene,wikipathways.pathway_name

"**fields**" accepts any attributes (a.k.a fields) available from the geneset object. Multiple attributes should be seperated by commas. If an attribute is not available for a specific geneset object, it will be ignored. Note that the attribute names are case-sensitive.

Just like `geneset query service <query_service.html>`_, you can also pass a "**callback**" parameter to make a `JSONP <http://ajaxian.com/archives/jsonp-json-with-padding>`_ call.



Query parameters
-----------------

fields
""""""""
    Optional, can be a comma-separated fields to limit the fields returned from the geneset object. If "fields=all", all available fields will be returned. Note that it supports dot notation as well, e.g., you can pass "refseq.rna". Default: "fields=all".

callback
"""""""""
    Optional, you can pass a "**callback**" parameter to make a `JSONP <http://ajaxian.com/archives/jsonp-json-with-padding>` call.

filter
"""""""
    Alias for "fields" parameter.

dotfield
""""""""""
    Optional, can be used to control the format of the returned fields when passed "fields" parameter contains dot notation, e.g. "fields=refseq.rna". If "dofield" is true, the returned data object contains a single "refseq.rna" field, otherwise, a single "refseq" field with a sub-field of "rna". Default: false.

email
""""""
    Optional, if you are regular users of our services, we encourage you to provide us an email, so that we can better track the usage or follow up with you.


Returned object
---------------

A GET request like this::

    http://mygeneset.info/v1/gene/1017

should return a geneset object below:

.. container:: gene-object-containter

    .. include :: gene_object.json



Batch queries via POST
======================

Although making simple GET requests above to our geneset query service is sufficient in most of use cases,
there are some cases you might find it's more efficient to make queries in a batch (e.g., retrieving gene
annotation for multiple genes). Fortunately, you can also make batch queries via POST requests when you
need::


    URL: http://mygeneset.info/v1/gene
    HTTP method:  POST


Query parameters
----------------

ids
"""""
    Required. Accept multiple geneset ids seperated by comma, e.g., 'ids=1017,1018' or 'ids=695,ENSG00000123374'. Note that currently we only take the input ids up to **1000** maximum, the rest will be omitted.

fields
"""""""
    Optional, can be a comma-separated fields to limit the fields returned from the matching hits.
    If “fields=all”, all available fields will be returned. Note that it supports dot notation as well, e.g., you can pass "refseq.rna". Default: “symbol,name,taxid,entrezgene”.

species
"""""""""""
    Optional, can be used to limit the gene hits to a given species. You can use "common names" for 17 common species. All other species, you can provide their taxonomy ids. See `more details here <data.html#species>`_. Multiple species can be passed using comma as a separator. Passing "all" will query against all available species. Default: all.

dotfield
""""""""""
    Optional, can be used to control the format of the returned fields when passed "fields" parameter contains dot notation, e.g. "fields=refseq.rna". If "dofield" is true, the returned data object contains a single "refseq.rna" field, otherwise, a single "refseq" field with a sub-field of "rna". Default: false.

email
""""""
    Optional, if you are regular users of our services, we encourage you to provide us an email, so that we can better track the usage or follow up with you.

Example code
------------

Unlike GET requests, you can easily test them from browser, make a POST request is often done via a
piece of code, still trivial of course. Here is a sample python snippet::

    import requests
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    params = 'ids=WP60,WP100&fields=name,taxid,genes.symbol'
    res = requests.post('http://mygeneset.info/v1/geneset', data=params, headers=headers)

Returned object
---------------

The returned result (the value of "res.text") from the example code above should look like this:

.. code-block:: json

    [
      {
	"query": "WP60",
	"_id": "WP60",
	"_version": 1,
	"genes": [
	  {
	    "symbol": "AAD15"
	  },
	  {
	    "symbol": "AAD6"
	  },
	  {
	    "symbol": "AAD14"
	  },
	  {
	    "symbol": "AAD3"
	  },
	  {
	    "symbol": "AAD10"
	  },
	  {
	    "symbol": "AAD4"
	  }
	],
	"name": "Toluene degradation",
	"taxid": 559292
      },
      {
	"query": "WP100",
	"_id": "WP100",
	"_version": 1,
	"genes": [
	  {
	    "symbol": "GGT2"
	  },
	  {
	    "symbol": "GGTLC2"
	  },
	  {
	    "symbol": "ANPEP"
	  },
	  {
	    "symbol": "OPLAH"
	  },
	  {
	    "symbol": "GSTA5"
	  },
	  {
	    "symbol": "GGTLC1"
	  },
	  {
	    "symbol": "IDH1"
	  },
	  {
	    "symbol": "GPX3"
	  },
	  {
	    "symbol": "GSTM1"
	  },
	  {
	    "symbol": "GPX2"
	  },
	  {
	    "symbol": "GGT1"
	  },
	  {
	    "symbol": "GPX1"
	  },
	  {
	    "symbol": "GSTT2"
	  },
	  {
	    "symbol": "GGT5"
	  },
	  {
	    "symbol": "LOC102724197"
	  },
	  {
	    "symbol": "GCLM"
	  },
	  {
	    "symbol": "GSTA1"
	  },
	  {
	    "symbol": "GCLC"
	  },
	  {
	    "symbol": "GSS"
	  },
	  {
	    "symbol": "GSR"
	  },
	  {
	    "symbol": "GSTM2"
	  },
	  {
	    "symbol": "G6PD"
	  },
	  {
	    "symbol": "GPX4"
	  }
	],
	"name": "Glutathione metabolism",
	"taxid": 9606
      }
    ]


.. raw:: html

    <div id="spacer" style="height:300px"></div>
