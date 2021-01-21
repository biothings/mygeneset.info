#!/usr/bin/env python3

import os
import requests

import mygene
from biothings.utils.dataload import dict_sweep, unlist

try:                         # run as a data plugin module of Biothings SDK
    from kegg.config_kegg import BASE_URL, LOG_LEVEL, organisms
    from biothings import config
    logging = config.logger
except Exception:            # run locally as a standalone script
    from config_kegg import BASE_URL, LOG_LEVEL, organisms
    import logging
    logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s: %(message)s')


def get_url_text_lines(url):
    """
    Send a request to `url` and return its plain text content in multiple lines.
    """

    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception(f"Failed to request {url}")

    text_lines = resp.text.strip('\n').split('\n')
    return text_lines


def get_shared_genesets(geneset_type):
    """
    Get genesets that are shared by all organisms and whose type is
    `geneset_type`.
    Note that the contents of URL response are tab-delimited.
    """
    url = BASE_URL + f"list/{geneset_type}"
    text_lines = get_url_text_lines(url)

    shared_genesets = dict()
    for line in text_lines:
        tokens = line.strip('\n').split("\t")
        entry = tokens[0].split(":")[1]
        name = tokens[1]
        shared_genesets[entry] = {
            'id': tokens[0],
            'type': geneset_type,
            'name': name
        }

    return shared_genesets


def get_pathway_genesets(organism_code):
    """
    Get pathway geneset names based on response from a request to KEGG
    list API.
    """

    pathway_genesets = dict()

    url = BASE_URL + f"list/pathway/{organism_code}"
    text_lines = get_url_text_lines(url)
    for line in text_lines:
        tokens = line.split("\t")
        entry = tokens[0].split(":")[1]
        name = tokens[1]
        if entry in pathway_genesets:
            raise Exception(f"Duplicate entry in {url}: {entry}")
        pathway_genesets[entry] = {
            'id': tokens[0],
            'type': 'pathway',
            'name': name,
        }

    return pathway_genesets


def query_mygene(genes, tax_id, gene_id_types):
    """Query MyGene.info to get detailed gene information."""

    genes_info = list()
    q_genes = genes
    output_fields = ['entrezgene', 'ensembl.gene', 'symbol', 'uniprot']

    mg = mygene.MyGeneInfo()
    for gid_type in gene_id_types:
        logging.info(f"Querying {gid_type} in MyGene.info ...")
        q_results = mg.querymany(
            q_genes,
            scopes=gid_type,
            fields=output_fields,
            species=tax_id,
            returnall=True
        )
        # For queries before the last one, only add valid results to `genes_info`;
        # For the last query, add all results to it.
        if gid_type != gene_id_types[-1]:
            genes_info += [g for g in q_results['out'] if not g.get('notfound', None)]
        else:
            genes_info += q_results['out']

        # Make sure that each query in MyGene.info returns one and only one match
        if len(q_results['dup']):
            raise Exception(f"Duplicate query results found: {q_results['dup']}")

        q_genes = q_results['missing']
        if len(q_genes) == 0:
            break

    # Debugging: print out the genes that are not found in mygene.info
    if len(q_genes):
        logging.info(f"{len(q_genes)} gene(s) missed when tax_id={tax_id}: {q_genes}")

    return genes_info


def load_data(data_dir):
    """The argument `data_dir` is not being used at this moment."""

    shared_diseases = get_shared_genesets("disease")
    shared_modules = get_shared_genesets("module")
    shared_genesets = {**shared_diseases, **shared_modules}

    for config in organisms:
        organism_name = config['name']
        tax_id = config['tax_id']

        logging.info("=" * 60)
        logging.info(f"Parsing genesets for {organism_name} (taxid={tax_id}) ...")

        organism_code = config['organism_code']

        pathway_genesets = get_pathway_genesets(organism_code)
        all_genesets = {**shared_genesets, **pathway_genesets}

        uniq_genes = set()
        genes_in_gs = dict()
        for gs_type in config['geneset_types']:
            url = BASE_URL + f"link/{organism_code}/{gs_type}"
            text_lines = get_url_text_lines(url)
            for line in text_lines:
                tokens = line.split()
                if gs_type == 'module':
                    gs_entry = tokens[0].split(":")[1].split("_")[1]
                else:
                    gs_entry = tokens[0].split(":")[1]

                if gs_entry not in genes_in_gs:
                    genes_in_gs[gs_entry] = list()

                gene = tokens[1].split(':')[1]
                genes_in_gs[gs_entry].append(gene)
                uniq_genes.add(gene)

        gene_id_types = config['gene_id_types']
        matched_genes = query_mygene(uniq_genes, tax_id, gene_id_types)

        # Build a map whose key is query string, value is gene info object
        q_to_geneinfo = dict()
        for gene in matched_genes:
            q_str = gene['query']
            ensembl_id = None  # ensembl_id is optional
            if 'ensembl' in gene and 'gene' in gene['ensembl']:
                ensembl_id = gene['ensembl']['gene']

            # Only keep 'Swiss-Prot' component in 'uniprot'
            uniprot = gene.get('uniprot', None)
            if uniprot:
               uniprot = uniprot.get('Swiss-Prot', None)

            q_to_geneinfo[q_str] = {
                'mygene_id': gene.get('_id', None),
                'ncbigene': gene.get('entrezgene', None),
                'ensemblgene': ensembl_id,
                'symbol': gene.get('symbol', None),
                'uniprot': uniprot
            }

        for gs_entry, genes in genes_in_gs.items():
            gs_id = all_genesets[gs_entry]['id']
            gs_type = all_genesets[gs_entry]['type']

            # If geneset is a "module", add organism code at the end of
            # its ID to make it unique.
            if gs_type == 'module':
                gs_id = gs_id + ":" + organism_code

            gs_name = all_genesets[gs_entry]['name']
            my_geneset = {
                '_id': f"KEGG_{gs_type}_{gs_entry}_{tax_id}",
                'is_public': True,
                'taxid': tax_id,
                'genes': [q_to_geneinfo[g] for g in genes],
                'kegg': {
                    'id': gs_id,
                    'database': gs_type,
                    'entry': gs_entry,
                    'name': gs_name,
                    'organism_code': organism_code,
                }
            }

            # Clean up the dict
            my_geneset = dict_sweep(my_geneset, vals=[None], remove_invalid_list=True)
            my_geneset = unlist(my_geneset)

            yield my_geneset


# Test harness
if __name__ == '__main__':
    import json

    # Time to create 9 organisms: 5-6 minutes (~5,300 genesets)
    for gs in load_data(None):
        print(json.dumps(gs, indent=2))
