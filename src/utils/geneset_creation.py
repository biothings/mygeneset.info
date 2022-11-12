"""Utility functions for creating and editing user genesets."""

import random


def generate_geneset_id():
    """Generate short random geneset ids."""
    # Generate six random integers between 0 and 61
    random_ints = [random.randint(0, 61) for _ in range(6)]
    # Convert to BASE62
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base62str = "".join([alphabet[i] for i in random_ints])
    return f"mygst:{base62str}"


def get_gene_list(geneset):
    """Get the genes from a geneset, always return a list."""
    # No genes
    if geneset.get('genes') is None:
        genes = []
    # Single gene
    elif not isinstance(geneset['genes'], list):
        genes = [geneset['genes']]
    # Multiple genes
    else:
        genes = geneset['genes']
    return genes


def update_taxid(geneset):
    """Annotate toplevel 'taxid' field in a geneset document.
    This field should be a list of all unique taxids in the geneset,
    When we add/remove genes from a geneset, we need to update this field.
    """
    unique_species = set([gene['taxid'] for gene in geneset['genes']])
    if len(unique_species) == 1:
        geneset['taxid'] = list(unique_species)[0]
    else:
        geneset['taxid'] = list(unique_species)
    return geneset
