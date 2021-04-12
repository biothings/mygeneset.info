Geneset query service
******************************

.. role:: raw-html(raw)
   :format: html
.. |info| image:: /_static/information.png
             :alt: information!


This page describes the reference for MyGeneset.info geneset query web service. It's also recommended to try it live on our `interactive API page <http://mygeneset.info/v1/api>`_.


Service endpoint
=================

::

    http://mygeneset.info/v1/query

GET request
==================

Query parameters
-----------------

q
"""""
    Required, passing user query. The detailed query syntax for parameter "**q**" we explained `below <#query-syntax>`_.

fields
""""""
    Optional, can be a comma-separated list of fields to limit the fields returned from the matching geneset hits. The supported field names can be found from any geneset object (e.g. `geneset WP60 <http://mygeneset.info/v1/geneset/WP60>`_). Note that it supports dot notation as well, e.g., you can pass "genes.symbol". If "fields=all", all available fields will be returned. Default:
    "_id,genes,name,description,source,author,date,is_public,taxid".

species
"""""""
    Optional, can be used to limit the geneset hits from given species. You can use "common names" for `17 common species <data.html#species-filter>`_. For all other species, you can provide their taxonomy ids. Multiple species can be passed using comma as a separator. Passing "all" will query against all available species. Default: all.

size
""""
    Optional, the maximum number of matching geneset hits to return (with a cap of 1000 at the moment). Default: 10.

from
""""
    Optional, the number of matching geneset hits to skip, starting from 0. Default: 0

.. Hint:: The combination of "**size**" and "**from**" parameters can be used to get paging for a large query:

::

    q=cdk*&size=50                     first 50 hits
    q=cdk*&size=50&from=50             the next 50 hits

fetch_all
"""""""""
    Optional, a boolean, which when TRUE, allows fast retrieval of all unsorted query hits.  The return object contains a **_scroll_id** field, which when passed as a parameter to the query endpoint, returns the next 1000 query results.  Setting **fetch_all** = TRUE causes the results to be inherently unsorted, therefore the **sort** parameter is ignored.  For more information see `examples using fetch_all here <#scrolling-queries>`_.  Default: FALSE.

scroll_id
"""""""""
    Optional, a string containing the **_scroll_id** returned from a query request with **fetch_all** = TRUE.  Supplying a valid **scroll_id** will return the next 1000 unordered results.  If the next results are not obtained within 1 minute of the previous set of results, the **scroll_id** becomes stale, and a new one must be obtained with another query request with **fetch_all** = TRUE.  All other parameters are ignored when the **scroll_id** parameter is supplied.  For more information see `examples using scroll_id here <#scrolling-queries>`_.

sort
""""
    Optional, the comma-separated fields to sort on. Prefix with "-" for descending order, otherwise in ascending order. Default: sort by matching scores in descending order.

facets
""""""
    Optional, a single field or comma-separated fields to return facets, for example, "facets=taxid", "facets=taxid,source". See `examples of faceted queries here <#faceted-queries>`_.

facet_size
""""""""""
    Optional, an integer (1 <= **facet_size** <= 1000) that specifies how many buckets to return in a faceted query.

species_facet_filter
""""""""""""""""""""
    Optional, relevant when faceting on species (i.e., "facets=taxid" are passed). It's used to pass species filter without changing the scope of faceting, so that the returned facet counts won't change. Either species name or taxonomy id can be used, just like "`species <#species>`_" parameter above. See `examples of faceted queries here <#faceted-queries>`_.


always_list
"""""""""""
    Optional, forces a field, or set of fields to always return an array. This is useful for fields such as **genes** and **genes.ensemblgene**, which may return an array or string. Can take a comma sepparated list of fields such as: "always_list=genes,genes.ensemblgene".

allow_null
""""""""""
    Optional, forces a field, or set of fields to return "**Null**" if the field does not exist. Can take a comma sepparated list of fields such as: "allow_null=genes.ncbigene,genes.ensemblgene".

callback
""""""""
    Optional, you can pass a "**callback**" parameter to make a JSONP call.

dotfield
""""""""
    Optional, can be used to control the format of the returned geneset object.  If "dotfield" is true, the returned data object is returned flattened (no nested objects) using dotfield notation for key names.  Default: false.

filter
""""""
    Alias for "fields" parameter.

limit
"""""
    Alias for "size" parameter.

skip
""""
    Alias for "from" parameter.

email
""""""
    Optional, if you are regular users of our services, we encourage you to provide us an email, so that we can better track the usage or follow up with you.


Query syntax
------------
Examples of query parameter "**q**":


Simple queries
""""""""""""""

search for everything::

    q=glucose                           search for any fields
    q=tumor suppressor                  default as "AND" for all query terms
    q="cyclin-dependent kinase"         search for the phrase



Fielded queries
"""""""""""""""
::

    q=genes.entrezgene:1017
    q=genes.symbol:cdk2
    q=source:reactome
    q=kegg.id:"path:hsa04723"

.. _available_fields:

Available fields
^^^^^^^^^^^^^^^^

This table lists some commonly used fields can be used for "fielded queries". Check out http://mygeneset.info/v1/metadata/fields for the complete list of available fields.

=======================    =======================================    =================================================================================
Field                      Description                                Examples
=======================    =======================================    =================================================================================
**name**                   Geneset name                               `q=name:kinase <http://mygeneset.info/v1/query?q=name:kinase>`_
**description**            Geneset description                        `q=description:cytosine deamination <http://mygeneset.info/v1/query?q=description:cytosine deamination>`_
**source**                 Name of data source (if built-in)          `q=source:kegg <http://mygeneset.info/v1/query?q=source:kegg>`_
**author**                 Geneset creator (if user-created)          `q=author:biothings <http://mygeneset.info/v1/query?q=author:biothings>`_
**taxid**                  Taxonomic id                               `q=taxid:9606 <http://mygeneset.info/v1/query?q=taxid:9606>`_
**genes.symbol**           HGNC gene symbol                           `q=genes.symbol:cdk1 <http://mygeneset.info/v1/query?q=genes.symbol:cdk1>`_
**genes.ncbigene**         NCBI gene id                               `q=genes.ncbigene:1017 <http://mygeneset.info/v1/query?q=genes.ncbigene:1017>`_
**genes.ensemblgene**      Ensembl gene id                            `q=genes.ensemblgene:ENSG00000123374 <http://mygeneset.info/v1/query?q=genes.ensemblgene:ENSG00000123374>`_
**genes.name**             Gene name                                  `q=genes.name:cyclin-dependent <http://mygeneset.info/v1/query?q=genes.name:cyclin-dependent>`_
**genes.uniprot**          UniProt SwissProt ID                       `q=genes.uniprot:P24941 <http://mygeneset.info/v1/query?q=genes.uniprot:P24941>`_
**genes.mygene_id**        MyGene.info primary gene _id               `q=genes.mygene_id:30 <http://mygeneset.info/v1/query?q=genes.my_gene_id:30>`_
**go.id**                  Gene Ontology id                           `q=go.id:GO_0042753 <http://mygeneset.info/v1/query?q=go.id:GO_0042753>`_
**kegg.id**                KEGG id                                    `q=kegg.id:"ds:H01348" <http://mygeneset.info/v1/query?q=kegg.id:"ds:H01348">`_
**wikipathways.id**        Wikipathways id                            `q=wikipathways.id:WP60 <http://mygeneset.info/v1/query?q=WP60>`_
**msigdb.id**              MSigDB id                                  `q=msigdb.id:CCATCCA_MIR432 <http://mygeneset.info/v1/query?q=msigdb.id:CCATCCA_MIR432>`_
**do.id**                  Disease Ontology id                        `q=do.id:DOID_0111329 <http://mygeneset.info/v1/query?q=do.id:DOID_0111329>`_
**ctd.id**                 CTD chemical id                            `q=ctd.id:C016705_9606 <http://mygeneset.info/v1/query?q=ctd.id:C016705_9606>`_
**ctd.cas**                chemical CAS id                            `q=ctd.cas:62-55-5 <http://mygeneset.info/v1/query?q=ctd.cas:62-55-5>`_
**ctd.mesh**               chemical mesh id                           `q=ctd.mesh:C016705 <http://mygeneset.info/v1/query?q=ctd.mesh:C016705>`_
**ctd.chemical_name**      chemical name                              `q=ctd.chemical_name:acetaminophen <http://mygeneset.info/v1/query?q=ctd.chemical_name:acetaminophen>`_
=======================    =======================================    =================================================================================


Wildcard queries
""""""""""""""""
Wildcard character "*" or "?" is supported in either simple queries or fielded queries::

    q=CDK?                              single character wildcard
    q=genes.symbol:CDK?                       single character wildcard within "symbol" field
    q=IL*R                              multiple character wildcard

.. note:: Wildcard character can not be the first character. It will be ignored.


Boolean operators and grouping
""""""""""""""""""""""""""""""

You can use **AND**/**OR**/**NOT** boolean operators and grouping to form complicated queries::

    q=tumor AND suppressor                        AND operator
    q=genes.symbol:CDK2 OR BTK                    OR operator
    q="tumor suppressor" NOT receptor             NOT operator
    q=(interleukin OR insulin) AND receptor       the use of parentheses


Returned object
---------------

A GET request like this::

    http://mygeneset.info/v1/query?q=genes.symbol:cdk2

should return hits as:

.. code-block:: json

    {
      "hits": [
        {
          "_id": "C016805_9606",
          "_score": 7.2883334,
          "genes": ["..."],
          "is_public": true,
          "taxid": "9606"
        },
        {
          "_id": "C017690_9606",
          "_score": 7.2883334,
          "genes": ["..."],
          "is_public": true,
          "taxid": "9606"
        },
        {
          "_id": "C017875_9606",
          "_score": 7.2883334,
          "genes": ["..."],
          "is_public": true,
          "taxid": "9606"
        }
      ]
    }


Faceted queries
----------------
If you need to perform a faceted query, you can pass an optional "`facets <#facets>`_" parameter. For example, if you want to get the facets on species, you can pass "facets=taxid":

A GET request like this::

    http://mygeneset.info/v1/query?q=glugose&size=1&facets=taxid

should return hits as:

.. code-block:: json

    {
      "hits":[
        {"..."}
      ],
      "total":26,
      "max_score":400.43347,
      "took":7,
      "facets":{
        "taxid":{
          "_type":"terms",
          "total":26,
          "terms":[
            {
              "count":14,
              "term":9606
            },
            {
              "count":7,
              "term":10116
            },
            {
              "count":5,
              "term":10090
            }
          ],
          "other":0,
          "missing":0
        }
      }
    }

Another useful field to get facets on is "type_of_gene"::

    http://mygeneset.info/v1/query?q=cdk2&size=1&facets=type_of_gene

It should return hits as:

.. code-block:: json
    :emphasize-lines: 15-32

    {
      "hits":[
        {
          "entrezgene":1017,
          "name":"cyclin-dependent kinase 2",
          "_score":400.43347,
          "symbol":"CDK2",
          "_id":"1017",
          "taxid":9606
        }
      ],
      "total":26,
      "max_score":400.43347,
      "took":97,
      "facets":{
        "type_of_gene":{
          "_type":"terms",
          "total":26,
          "terms":[
            {
              "count":20,
              "term":"protein-coding"
            },
            {
              "count":6,
              "term":"pseudo"
            }
          ],
          "other":0,
          "missing":0
        }
      }
    }

If you need to, you can also pass multiple fields as comma-separated list::

    http://mygeneset.info/v1/query?q=cdk2&size=1&facets=taxid,type_of_gene


Particularly relevant to species facets (i.e., "facets=taxid"), you can pass a
"`species_facet_filter <#species_facet_filter>`_" parameter to filter the returned hits on a given species, without changing the scope of the facets (i.e. facet counts will not change). This is useful when you need to get the subset of the hits for a given species after the initial faceted query on species.

You can see the different "hits" are returned in the following queries, while "facets" keeps the same::

    http://mygeneset.info/v1/query?q=cdk?&size=1&facets=taxid&species_facet_filter=human

v.s.
::

    http://mygeneset.info/v1/query?q=cdk?&size=1&facets=taxid&species_facet_filter=mouse


Scrolling queries
-----------------
If you want to return ALL results of a very large query (>10,000 results), sometimes the paging method described `above <#from>`_ can take too long.  In these cases, you can use a scrolling query.
This is a two-step process that turns off database sorting to allow very fast retrieval of all query results.  To begin a scrolling query, you first call the query
endpoint as you normally would, but with an extra parameter **fetch_all** = TRUE.  For example, a GET request to::

    http://mygeneset.info/v1/query?q=brain&fetch_all=TRUE

Returns the following object:

.. code-block:: json

    {
      "_scroll_id": "cXVlcnlUaGVuRmV0Y2g7MTA7MjA1NjY1MzMwOl9HM29rRkg2VFZ5S1c3cTJtYkI4RHc7MjA1NjY1MjY3OlM0V1VCa194UWdLYjlQWTR5NGZCeFE7MjA1NjY1MTM0OlRGWVpXLVZrU2NTWmZLQUlEVnlRRkE7MjA1NjY1MzMxOl9HM29rRkg2VFZ5S1c3cTJtYkI4RHc7MzEyMDY0NzU6TVBZd0FEVF9UcVdSQWhWajlfN2U4ZzsyMDU2NjUxMzM6VEZZWlctVmtTY1NaZktBSURWeVFGQTsyMDU2NjUxMzU6VEZZWlctVmtTY1NaZktBSURWeVFGQTsyMDU2NjUzMzI6X0czb2tGSDZUVnlLVzdxMm1iQjhEdzsyMDU2NjUyNjg6UzRXVUJrX3hRZ0tiOVBZNHk0ZkJ4UTszMTIwNjQ3NDpNUFl3QURUX1RxV1JBaFZqOV83ZThnOzA7",
      "max_score": 13.958638,
      "took": 270,
      "total": 14571,
      "hits": [
        {
          "_id": "390259",
          "_score": 13.958638,
          "entrezgene": 390259,
          "name": "brain specific homeobox",
          "symbol": "BSX",
          "taxid": 9606
        },
        .
        .
        .
      ]
    }

At this point, the first 1000 hits have been returned (of ~14,000 total), and a scroll has been set up for your query.  To get the next batch of 1000 unordered results, simply execute a GET request to the following address, supplying the _scroll_id from the first step into the **scroll_id** parameter in the second step::

    http://mygeneset.info/v1/query?scroll_id=cXVlcnlUaGVuRmV0Y2g7MTA7MjA1NjY1MzMwOl9HM29rRkg2VFZ5S1c3cTJtYkI4RHc7MjA1NjY1MjY3OlM0V1VCa194UWdLYjlQWTR5NGZCeFE7MjA1NjY1MTM0OlRGWVpXLVZrU2NTWmZLQUlEVnlRRkE7MjA1NjY1MzMxOl9HM29rRkg2VFZ5S1c3cTJtYkI4RHc7MzEyMDY0NzU6TVBZd0FEVF9UcVdSQWhWajlfN2U4ZzsyMDU2NjUxMzM6VEZZWlctVmtTY1NaZktBSURWeVFGQTsyMDU2NjUxMzU6VEZZWlctVmtTY1NaZktBSURWeVFGQTsyMDU2NjUzMzI6X0czb2tGSDZUVnlLVzdxMm1iQjhEdzsyMDU2NjUyNjg6UzRXVUJrX3hRZ0tiOVBZNHk0ZkJ4UTszMTIwNjQ3NDpNUFl3QURUX1RxV1JBaFZqOV83ZThnOzA7

.. Hint:: Your scroll will remain active for 1 minute from the last time you requested results from it.  If your scroll expires before you get the last batch of results, you must re-request the scroll_id by setting **fetch_all** = TRUE as in step 1.


Batch queries via POST
======================

Although making simple GET requests above to our geneset query service is sufficient in most of use cases,
there are some cases you might find it's more efficient to make queries in a batch (e.g., retrieving gene
annotation for multiple genes). Fortunately, you can also make batch queries via POST requests when you
need::


    URL: http://mygeneset.info/v1/query
    HTTP method:  POST


Query parameters
----------------

q
"""
    Required, multiple query terms seperated by comma (also support "+" or white space), but no wildcard, e.g., 'q=1017,1018' or 'q=CDK2+BTK'

scopes
""""""
    Optional, specify one or more fields (separated by comma) as the search "scopes", e.g., "scopes=entrezgene",
    "scopes=entrezgene,ensemblgene". The available "fields" can be passed to "**scopes**" parameter are
    :ref:`listed above <available_fields>`. Default: "scopes=entrezgene,ensemblgene,retired" (either Entrez
    or Ensembl gene ids).

species
"""""""
     Optional, can be used to limit the gene hits from given species. You can use "common names" for nine common species (human, mouse, rat, fruitfly, nematode, zebrafish, thale-cress, frog and pig). All other species, you can provide their taxonomy ids. See `more details here <data.html#species>`_. Multiple species can be passed using comma as a separator. Default: all.

fields
""""""
    Optional, can be a comma-separated fields to limit the fields returned from the matching gene hits. The supported field names can be found from any gene object (e.g. `gene 1017 <http://mygeneset.info/v1/gene/1017>`_). Note that it supports dot notation as well, e.g., you can pass "refseq.rna". If "fields=all", all available fields will be returned. Default:
    "symbol,name,taxid,entrezgene".

dotfield
""""""""""
    Optional, can be used to control the format of the returned fields when passed "fields" parameter contains dot notation, e.g. "fields=refseq.rna". If "dofield" is true, the returned data object contains a single "refseq.rna" field, otherwise, a single "refseq" field with a sub-field of "rna". Default: false.

email
""""""
    Optional, if you are regular users of our services, we encourage you to provide us an email, so that we can better track the usage or follow up with you.

Example code
------------

Unlike GET requests, you can easily test them from browser, make a POST request is often done via a
piece of code. Here is a sample python snippet::

    import requests
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    params = 'q=1017,1018&scopes=entrezgene&fields=name,symbol,taxid,entrezgene'
    res = requests.post('http://mygeneset.info/v1/query', data=params, headers=headers)


Returned object
---------------

Returned result (the value of "res.text" variable above) from above example code should look like this:

.. code-block:: json

    [
      {
        '_id': '1017',
        '_score': 22.757837,
        'entrezgene': 1017,
        'name': 'cyclin dependent kinase 2',
        'query': '1017',
        'symbol': 'CDK2',
        'taxid': 9606
      },
      {
        '_id': '1018',
        '_score': 22.757782,
        'entrezgene': 1018,
        'name': 'cyclin dependent kinase 3',
        'query': '1018',
        'symbol': 'CDK3',
        'taxid': 9606
      }
    ]


.. Tip:: "query" field in returned object indicates the matching query term.
.. Note:: if no "fields" parameter is specified, all available fields will be returned

If a query term has no match, it will return with "**notfound**" field as "**true**"::

    params = 'q=1017,dummy&scopes=entrezgene&fields=name,symbol,taxid,entrezgene'
    res = requests.post('http://mygeneset.info/v1/query', data=params, headers=headers)

.. code-block:: json
    :emphasize-lines: 12

    [
      {
        "name": "cyclin-dependent kinase 2",
        "symbol": "CDK2",
        "taxid": 9606,
        "entrezgene": 1017,
        "query": "1017",
        "_id": "1017"
      },
      {
        "query": "dummy",
        "notfound": true
      }
    ]

If a query term has multiple matches, they will be included with the same "query" field::

    params = 'q=tp53,1017&scopes=symbol,entrezgene&fields=name,symbol,taxid,entrezgene'
    res = requests.post('http://mygeneset.info/v1/query', data=params, headers=headers)


.. code-block:: json
    :emphasize-lines: 7,15

    [
      {
        "name": "tumor protein p53",
        "symbol": "TP53",
        "taxid": 9606,
        "entrezgene": 7157,
        "query": "tp53",
        "_id": "7157"
      },
      {
        "name": "tumor protein p53",
        "symbol": "Tp53",
        "taxid": 10116,
        "entrezgene": 24842,
        "query": "tp53",
        "_id": "24842"
      },
      {
        "name": "cyclin-dependent kinase 2",
        "symbol": "CDK2",
        "taxid": 9606,
        "entrezgene": 1017,
        "query": "1017",
        "_id": "1017"
      }
    ]







.. raw:: html

    <div id="spacer" style="height:300px"></div>
