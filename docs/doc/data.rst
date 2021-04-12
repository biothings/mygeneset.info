.. Data

Geneset annotation data
***********************

.. _data_sources:

Data sources
------------

We currently obtain the geneset annotation data from several public data resources and keep them up-to-date, so that you don't have to do it:

==================   =======================
Source               Update frequency
==================   =======================
MSigDB               whenever a new
                     release is available
Gene Ontology        whenever a new
                     release is available
KEGG                 whenever a new
                     release is available
WikiPathways         whenever a new
                     release is available
Reactome             whenever a new
                     release is available
Disease Ontology     whenever a new
                     release is available

==================   =======================

The most updated data information can be accessed `here <http://mygeneset.info/v1/metadata>`__.

.. _gene_object:

Geneset object
--------------
Geneset annotation data are both stored and returned as a geneset object, which is essentially a collection of fields (attributes) and their values:

.. code-block :: json

    {
      "_id": "WP60",
      "_version": 1,
      "genes": [
        {
          "ensemblgene": "YOL165C",
          "mygene_id": "853999",
          "name": "putative aryl-alcohol dehydrogenase",
          "ncbigene": "853999",
          "symbol": "AAD15",
          "uniprot": "Q08361"
        },
        {
          "mygene_id": "850488",
          "name": "pseudo",
          "ncbigene": "850488",
          "symbol": "AAD6"
        },
        {
          "ensemblgene": "YNL331C",
          "mygene_id": "855385",
          "name": "putative aryl-alcohol dehydrogenase",
          "ncbigene": "855385",
          "symbol": "AAD14",
          "uniprot": "P42884"
        },
        {
          "ensemblgene": "YCR107W",
          "mygene_id": "850471",
          "name": "putative aryl-alcohol dehydrogenase",
          "ncbigene": "850471",
          "symbol": "AAD3",
          "uniprot": "P25612"
        },
        {
          "ensemblgene": "YJR155W",
          "mygene_id": "853620",
          "name": "putative aryl-alcohol dehydrogenase",
          "ncbigene": "853620",
          "symbol": "AAD10",
          "uniprot": "P47182"
        },
        {
          "ensemblgene": "YDL243C",
          "mygene_id": "851354",
          "name": "putative aryl-alcohol dehydrogenase",
          "ncbigene": "851354",
          "symbol": "AAD4",
          "uniprot": "Q07747"
        }
      ],
      "is_public": true,
      "name": "Toluene degradation",
      "source": "wikipathways",
      "taxid": 559292,
    }

The example above contains the most common available fields, but omits some fields that are specific to specific data sources. For a full example, you can check out a few examples: `GO_0004568_9606 <http://mygeneset.info/v1/geneset/GO_0004568_9606>`_ (a Gene Ontology geneset), `WP60 <http://mygeneset.info/v1/geneset/WP60>`_ (a Wikipathways geneset), or find a list of the available fields at: http://mygeneset.info/v1/metadata/fields

_id field
---------

Each individual geneset object contains an "**_id**" field as the primary key. The value of the "**_id**" field is different for every built-in data source, but is typically the primary ID used in the source data. For example, for MSigDB, this is the original geneset id. For genesets coming from metabolic pathway databases (KEGG, GO, Wikipathways) which contain multiple species, **_id** is typically a combination of the pathway id, plus the organism taxid. User-submitted genesets have randomly generated **_id** fields. Here is `an example <http://mygeneset.info/v1/gene/ENSG00000274236>`_. If searching for a particular GO term, or KEGG ID using the query endpoint, we recommend using "**kegg.id**"or "**go.id**", plus the `species <data.html#species-filter>`_ filter instead of "**_id**".

.. note:: Regardless how the value of the "**_id**" field looks like, it always works for our geneset annotation service `/v1/geneset/\<geneid\> <annotation_service.html#get-request>`_.


_score field
------------
You will often see a "**_score**" field in the returned geneset object, which is the internal score representing how well the query matches the returned geneset object. It probably does not mean much in the `geneset annotation service <annotation_service.html>`_ when only one geneset object is returned. In the `geneset query 
service <query_service.html>`__, by default, the returned geneset hits are sorted by the scores in descending order.


.. _species:
Species filter
--------------
We support **ALL** species annotated by NCBI and Ensembl. All of our services allow you to pass a "**species**" parameter to limit the query results. "species" parameter accepts taxonomy ids as the input. You can look for the taxomony ids for your favorite species from `NCBI Taxonomy <http://www.ncbi.nlm.nih.gov/taxonomy>`_.

For convenience, we allow you to pass these *common names* for commonly used species (e.g. "species=human,mouse,rat"):

.. container:: species-table


    =========================   ========================     ===========
    Search term (common name)   Genus name                   Taxonomy id
    =========================   ========================     ===========
    human                       Homo sapiens                 9606
    mouse                       Mus musculus                 10090
    rat                         Rattus norvegicus            10116
    mosquito                    Anopheles gambiae            180454
    fruitfly                    Drosophila melanogaster      7227
    nematode                    Caenorhabditis elegans       6239
    zebrafish                   Danio rerio                  7955
    thale-cress                 Arabidopsis thaliana         3702
    rice                        Oryza sativa                 39947
    dog                         Canis lupus familiaris       9615
    chicken                     Gallus gallus                9031
    horse                       Equus caballus               9796
    chimpanzee                  Pan troglodytes              9598
    frog                        Xenopus tropicalis           8364
    pig                         Sus scrofa                   9823
    pseudomonas-aeruginosa      Pseudomonas aeruginosa       208964
    brewers-yeast               Saccharomyces cerevisiae     559292
    =========================   ========================     ===========


If needed, you can pass "species=all" to query against all available species, although, we recommend you to pass specific species you need for faster response.
