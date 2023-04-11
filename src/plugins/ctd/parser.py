#!/usr/bin/env python3

import os

from biothings.utils.dataload import dict_sweep, unlist

if __name__ == "__main__":
    # Run locally as a standalone script
    import logging
    import sys

    sys.path.append("../../")

    import config

    LOG_LEVEL = logging.WARNING
    logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s: %(message)s")

else:
    # Run as a data plugin module of Biothings SDK
    from biothings import config

    logging = config.logger

from utils.mygene_lookup import MyGeneLookup

# Organisms (key is species taxonomy ID, value is species common name)
organisms = {
    "6239": "worm",
    "7227": "fly",
    "7955": "zebrafish",
    "8364": "frog",
    "9031": "chicken",
    "9606": "human",
    "9615": "dog",
    "10090": "mouse",
    "10116": "rat",
}


def get_ctd_genesets(filename):
    """
    Reads the chemical–gene interactions tsv file, which includes 11 fields:
      (0)  ChemicalName
      (1)  ChemicalID (MeSH identifier)
      (2)  CasRN (CAS Registry Number, if available)
      (3)  GeneSymbol
      (4)  GeneID (NCBI Gene identifier)
      (5)  GeneForms ('|'-delimited list)
      (6)  Organism (scientific name)
      (7)  OrganismID (NCBI Taxonomy identifier)
      (8)  Interaction
      (9)  InteractionActions ('|'-delimited list)
      (10) PubMedIDs ('|'-delimited list)

    and returns the genetsets as a dict in this format:
      {
          tax_id: {
              'unique_genes': set,
              'genesets': {
                   chemical_id: {
                       'chemical_name': str,
                       'genes': set,
                       'cas_rn': str,
                   },
                   ... ...
              }
          }
      }
    """

    ctd_genesets = dict()
    with open(filename) as fh:
        for row_num, row in enumerate(fh, start=1):
            if row.startswith("#"):  # skip comment lines
                continue

            tokens = row.strip("\n").split("\t")
            if len(tokens) != 11:
                logging.warning(f"Line #{row_num} has {len(tokens)} columns, skipped")
                continue

            tax_id = tokens[7].strip()
            if tax_id not in organisms:
                continue

            chemical_name = tokens[0].strip()
            chemical_id = tokens[1].strip()
            gene_id = tokens[4].strip()
            entity_type = tokens[5].strip()

            if chemical_id is None or gene_id is None:
                continue

            if entity_type not in ["gene", "protein"]:
                continue

            cas_rn = tokens[2].strip()
            if len(cas_rn) == 0:
                cas_rn = None

            if tax_id not in ctd_genesets:
                ctd_genesets[tax_id] = {"unique_genes": set(), "genesets": dict()}
            # uique_genes contains all the unique genes for a given tax_id
            ctd_genesets[tax_id]["unique_genes"].add(gene_id)
            # genesets contains the geneset chemical ids and associated genes
            if chemical_id in ctd_genesets[tax_id]["genesets"]:
                ctd_genesets[tax_id]["genesets"][chemical_id]["genes"].add(gene_id)
            else:
                ctd_genesets[tax_id]["genesets"][chemical_id] = {
                    "chemical_name": chemical_name,
                    "cas_rn": cas_rn,
                    "genes": {gene_id},
                }

    return ctd_genesets


def load_data(data_dir):
    """Read CTD data file and yield genesets."""

    filename = os.path.join(data_dir, "CTD_chem_gene_ixns.tsv")
    ctd_genesets = get_ctd_genesets(filename)
    for tax_id, data in ctd_genesets.items():
        # 'data' dictionary contains the genesets for a given tax_id,
        # and all the unique genes for that tax_id
        organism_name = organisms[tax_id]
        logging.info("=" * 60)
        logging.info(f"Building '{organism_name}' genesets (taxid = {tax_id})")
        entrez_set = data["unique_genes"]

        # Lookup all unique genes for the organism.
        # Some genesets in CTD have homolog ids, so we must convert them to tax_id
        organism_genes = [str(gene) for gene in entrez_set]
        gene_lookup = MyGeneLookup(tax_id)
        gene_lookup.query_mygene_homologs(organism_genes, "entrezgene,retired", new_species=tax_id)

        # Build individual genesets
        genesets = data["genesets"]
        for chemical_id, ctd_info in genesets.items():
            gid_set = ctd_info["genes"]  # set of gene ids for this chemical
            genes = [str(gene) for gene in gid_set]

            # Get gene lookup results for all genes in this geneset
            lookup_results = gene_lookup.get_results(genes)

            chemical_name = ctd_info["chemical_name"]
            cas_rn = ctd_info["cas_rn"]
            my_geneset = dict()
            my_geneset["_id"] = chemical_id + "_" + tax_id
            my_geneset["is_public"] = True
            my_geneset["taxid"] = tax_id
            my_geneset["source"] = "ctd"
            my_geneset["name"] = f"{chemical_name} interactions"
            my_geneset[
                "description"
            ] = f"Chemical-gene interactions of {chemical_name} in {organism_name}"

            # CTD-specific fields
            my_geneset["ctd"] = {
                "id": chemical_id,
                "chemical_name": chemical_name,
                "mesh": chemical_id,
                "cas": cas_rn,
            }
            my_geneset.update(lookup_results)
            my_geneset = dict_sweep(my_geneset, vals=[None], remove_invalid_list=True)
            my_geneset = unlist(my_geneset)

            yield my_geneset


# Test harness
if __name__ == "__main__":
    import json

    from version import get_release

    # Get data dir
    version = get_release(None)
    data_dir = os.path.join(config.DATA_ARCHIVE_ROOT, "ctd", version)

    for gs in load_data(data_dir):
        print(json.dumps(gs, indent=2))
