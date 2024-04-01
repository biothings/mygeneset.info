#!/usr/bin/env python3

import requests
from biothings.utils.dataload import dict_sweep, unlist

try:
    # Run as a data plugin module of Biothings SDK
    from biothings import config
    from kegg.species import organisms
    from utils.mygene_lookup import MyGeneLookup

    logging = config.logger

except ImportError:
    # Run as a standalone script
    import logging
    import sys

    from species import organisms

    sys.path.append("../../")
    from utils.mygene_lookup import MyGeneLookup

    LOG_LEVEL = logging.DEBUG
    logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s: %(message)s")

BASE_URL = "http://rest.kegg.jp/"


def get_url_text_lines(url):
    """
    Send a request to `url` and return its plain text content
    in multiple lines.
    """
    resp = requests.get(url)
    resp.raise_for_status()
    text_lines = resp.text.strip("\n").split("\n")
    return text_lines


def get_shared_genesets(geneset_type):
    """
    Get genesets that are shared by all organisms and whose type is
    `geneset_type`, where geneset_type is one of: 'pathway' or 'module'.
    Each line is a disease/module id and name.
    Note that the contents of URL response are tab-delimited.
    """
    url = BASE_URL + f"list/{geneset_type}"
    text_lines = get_url_text_lines(url)

    shared_genesets = dict()
    for line in text_lines:
        tokens = line.strip("\n").split("\t")
        entry = tokens[0]
        name = tokens[1]
        shared_genesets[entry] = {"id": tokens[0], "type": geneset_type, "name": name}
    return shared_genesets


def get_pathway_genesets(organism_code):
    """
    Get pathway geneset names based on response from a request to KEGG
    list API.
    Each line is a pathway id and name.
    """
    pathway_genesets = dict()

    url = BASE_URL + f"list/pathway/{organism_code}"
    text_lines = get_url_text_lines(url)
    for line in text_lines:
        tokens = line.split("\t")
        entry = tokens[0]
        name = tokens[1]
        if entry in pathway_genesets:
            raise Exception(f"Duplicate entry in {url}: {entry}")
        pathway_genesets[entry] = {
            "id": tokens[0],
            "type": "pathway",
            "name": name,
        }
    return pathway_genesets


def get_unique_tokens(geneset_name):
    """
    Delimit the input `geneset_name` by "; ", and return a new string
    that includes only unique tokens delimited by "; ".
    """
    tokens = geneset_name.split("; ")
    uniq_tokens = []
    for t in tokens:
        if t not in uniq_tokens:
            uniq_tokens.append(t)
    return "; ".join(uniq_tokens)


def load_data(data_dir):
    """The argument `data_dir` is not being used at this moment.
    This dataset consists of three types of genesets:
    - disease: common disease-gene relationships found in all organisms
    - module: common "sub-pathways" found in all organisms
    - pathway: patways-gene relationships that can be organism specific
    """
    diseases = get_shared_genesets("disease")
    modules = get_shared_genesets("module")
    # Merge the two dictionaries
    shared_genesets = {**diseases, **modules}

    for conf in organisms:
        organism_name = conf["name"]
        tax_id = str(conf["tax_id"])

        logging.info("=" * 60)
        logging.info(f"Building '{organism_name}' genesets (taxid = {tax_id}) ...")

        organism_code = conf["organism_code"]

        pathway_genesets = get_pathway_genesets(organism_code)
        # all_genesets is a dictionary containing geneset id, type, and name
        all_genesets = {**shared_genesets, **pathway_genesets}

        uniq_genes = set()
        genes_in_gs = dict()
        for gs_type in conf["geneset_types"]:
            # Fetch file with genes/genesets for each type
            # Each row contains one geneset id and a single gene id
            url = BASE_URL + f"link/{organism_code}/{gs_type}"
            text_lines = get_url_text_lines(url)
            for line in text_lines:
                tokens = line.split("\t")
                # Get the geneset name
                if gs_type == "module":
                    gs_entry = tokens[0].split(":")[1].split("_")[1]
                else:
                    gs_entry = tokens[0].split(":")[1]

                if gs_entry not in genes_in_gs:
                    genes_in_gs[gs_entry] = list()
                # Append the gene id to the geneset dictionary
                gene = tokens[1].split(":")[1]
                genes_in_gs[gs_entry].append(gene)
                uniq_genes.add(gene)

        # Query mygene for all genes for this species
        gene_id_types = ",".join(conf["gene_id_types"])
        gene_lookup = MyGeneLookup(tax_id)
        gene_lookup.query_mygene(list(uniq_genes), gene_id_types)

        for gs_entry, genes in genes_in_gs.items():
            gs_type = all_genesets[gs_entry]["type"]
            gs_name = all_genesets[gs_entry]["name"]

            lookup_results = gene_lookup.get_results(genes)

            # Build geneset document
            my_geneset = {
                "_id": f"KEGG_{gs_type}_{gs_entry}_{tax_id}",
                "is_public": True,
                "taxid": tax_id,
                "source": "kegg",
                "name": get_unique_tokens(gs_name),
                "kegg": {
                    "id": gs_entry,
                    "database": gs_type,
                    "name": gs_name,
                    "organism_code": organism_code,
                },
            }

            # Add gene lookup results to geneset document
            my_geneset.update(lookup_results)

            # Clean up the dict
            my_geneset = dict_sweep(my_geneset, vals=[None], remove_invalid_list=True)
            my_geneset = unlist(my_geneset)

            yield my_geneset


# Test harness
if __name__ == "__main__":
    import json

    # Time to create 9 organisms: 5-6 minutes (~5,300 genesets)
    for gs in load_data(None):
        print(json.dumps(gs, indent=2))
