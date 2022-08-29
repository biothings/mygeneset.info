"""KEGG configuration module."""

# Possible gene_id_types:
#  * '_id'
#  * 'entrezgene'
#  * 'ensemblgene' (or 'ensembl.gene)
#  * 'symbol'
#  * 'locus_tag'
#  * 'uniprot'

organisms = [
    # arabidopsis
    {
        'name': 'arabidopsis',
        'tax_id': 3702,
        'organism_code': 'ath',
        'geneset_types': ['module', 'pathway'],
        'gene_id_types': ['locus_tag'],
    },

    # (fruit)fly
    {
        'name': 'fly',
        'tax_id': 7227,
        'organism_code': 'dme',
        'geneset_types': ['module', 'pathway'],
        'gene_id_types': ['locus_tag'],
    },

    # human
    {
        'name': 'human',
        'tax_id': 9606,
        'organism_code': 'hsa',
        'geneset_types': ['disease', 'module', 'pathway'],
        'gene_id_types': ['entrezgene', 'retired'],
    },

    # mouse
    {
        'name': 'mouse',
        'tax_id': 10090,
        'organism_code': 'mmu',
        'geneset_types': ['module', 'pathway'],
        'gene_id_types': ['entrezgene', 'retired'],
    },

    # pseudomonas
    {
        'name': 'pseudomonas',
        'tax_id': 208964,
        'organism_code': 'pae',
        'geneset_types': ['module', 'pathway'],
        'gene_id_types': ['locus_tag'],
    },

    # rat
    {
        'name': 'rat',
        'tax_id': 10116,
        'organism_code': 'rno',
        'geneset_types': ['module', 'pathway'],
        'gene_id_types': ['entrezgene', 'retired'],
    },

    # worm
    {
        'name': 'worm',
        'tax_id': 6239,
        'organism_code': 'cel',
        'geneset_types': ['module', 'pathway'],
        'gene_id_types': ['locus_tag', 'symbol'],

    },

    # yeast
    {
        'name': 'yeast',
        'tax_id': 559292,
        'organism_code': 'sce',
        'geneset_types': ['module', 'pathway'],
        'gene_id_types': ['locus_tag'],
    },

    # "zebrafish"
    {
        'name': 'zebrafish',
        'tax_id': 7955,
        'organism_code': 'dre',
        'geneset_types': ['module', 'pathway'],
        'gene_id_types': ['entrezgene', 'retired'],
    },

    # Add th following species that are NOT supported in Tribe?
    # - frog (8364)
    # - pig (9823)
]
