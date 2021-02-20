#!/usr/bin/env python3

import os

import mygene
from biothings.utils.dataload import dict_sweep, unlist

try:                         # run as a data plugin module of Biothings SDK
    from biothings import config
    logging = config.logger
except Exception:            # run locally as a standalone script
    import logging
    LOG_LEVEL=logging.DEBUG
    logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s: %(message)s')


# Organisms (key is species taxonomy ID, value is species common name)
organisms = {
    '7227': 'fly',
    '9606': 'human',
    '10090': 'mouse',
    '6239': 'nematode',
    '9823': 'pig',
    '10116': 'rat',
    '6239': 'worm',
    '7955': 'zebrafish',
}


def query_mygene(entrez_set, tax_id):
    """Query mygene.info to get detailed gene information."""

    q_genes = entrez_set
    q_scopes = ['entrezgene', 'retired']
    output_fields = ['entrezgene', 'ensembl.gene', 'symbol', 'uniprot']

    mg = mygene.MyGeneInfo()
    logging.info(f"Querying {q_scopes} in MyGene.info ...")
    q_results = mg.querymany(
        q_genes,
        scopes=q_scopes,
        fields=output_fields,
        species=tax_id,
        returnall=True
    )

    genes_info = dict()
    for gene in q_results['out']:
        q_str = gene["query"]
        if gene.get('notfound', None):  # ignore missing genes
            continue

        # Ensembl gene ID
        ensembl_gene = None
        ensembl = gene.get('ensembl', None)
        if ensembl and 'gene' in ensembl:
            ensembl_gene =  ensembl['gene']

        # Only keep 'Swiss-Prot' component in 'uniprot'
        uniprot = gene.get('uniprot', None)
        if uniprot:
            uniprot = uniprot.get('Swiss-Prot', None)

        genes_info[q_str] = {
            'mygene_id': gene.get('_id', None),
            'ncbigene': gene.get('entrezgene', None),
            'ensemblgene': ensembl_gene,
            'symbol': gene.get('symbol', None),
            'uniprot': uniprot
        }

    return genes_info


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

            tokens = row.strip('\n').split('\t')
            if len(tokens) != 11:
                logging.warning(f"Line #{row_num} has {len(tokens)} columns, skipped")
                continue

            tax_id = tokens[7]
            if tax_id not in organisms:
                continue

            chemical_name = tokens[0]
            chemical_id = tokens[1]
            gene_id = int(tokens[4])

            cas_rn = tokens[2].strip()
            if len(cas_rn) == 0:
                cas_rn = None

            if tax_id not in ctd_genesets:
                ctd_genesets[tax_id] = {
                    'unique_genes': set(),
                    'genesets': dict()
                }

            ctd_genesets[tax_id]['unique_genes'].add(gene_id)
            if chemical_id in ctd_genesets[tax_id]['genesets']:
                ctd_genesets[tax_id]['genesets'][chemical_id]['genes'].add(gene_id)
            else:
                ctd_genesets[tax_id]['genesets'][chemical_id] = {
                    'chemical_name': chemical_name,
                    'cas_rn': cas_rn,
                    'genes': {gene_id},
                }

    return ctd_genesets


def load_data(data_dir):
    """Read CTD data file and yield genesets."""

    filename = os.path.join(data_dir, "CTD_chem_gene_ixns.tsv")
    ctd_genesets = get_ctd_genesets(filename)
    for tax_id, value in ctd_genesets.items():
        organism_name = organisms[tax_id]
        logging.info(f"Building {organism_name} genesets (taxid = {tax_id})")
        entrez_set = value['unique_genes']
        genes_info = query_mygene(entrez_set, tax_id)

        genesets = value['genesets']
        for chemical_id, ctd_info in genesets.items():
            gid_set = ctd_info['genes']
            genes_found = [
                genes_info[str(gid)] for gid in sorted(gid_set) if str(gid) in genes_info
            ]
            # Ignore a geneset if none of its genes is found in mygene.info
            if len(genes_found) == 0:
                continue

            chemical_name = ctd_info['chemical_name']
            cas_rn = ctd_info['cas_rn']
            my_geneset = dict()
            my_geneset['_id'] = chemical_id + "-" + tax_id
            my_geneset['is_public'] = True
            my_geneset['taxid'] = tax_id
            my_geneset['genes'] = genes_found

            # CTD-specific fields
            my_geneset['ctd'] = {
                'id': my_geneset['_id'],
                'chemical_name': chemical_name,
                'mesh': chemical_id,
                'cas': cas_rn,
            }

            my_geneset = dict_sweep(my_geneset, vals=[None], remove_invalid_list=True)
            my_geneset = unlist(my_geneset)

            yield my_geneset


# Test harness
if __name__ == '__main__':
    import json

    for gs in load_data('./data'):
        print(json.dumps(gs, indent=2))
