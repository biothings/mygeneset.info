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
    '6239': 'worm',
    '7227': 'fly',
    '7955': 'zebrafish',
    "8364": "frog",
    "9031": "chicken",
    '9606': 'human',
    "9615": "dog",
    '10090': 'mouse',
    '10116': 'rat',
}


def polish_gene_info(gene):
    """Polish some field values in input gene."""

    ensembl = gene.get('ensembl', None)
    if ensembl:
        if len(ensembl) > 1:
            ensembl = [g['gene'] for g in ensembl if 'gene' in g]
        elif 'gene' in ensembl:
            ensembl = ensembl['gene']

    # Only keep 'Swiss-Prot' component in 'uniprot'
    uniprot = gene.get('uniprot', None)
    if uniprot:
        uniprot = uniprot.get('Swiss-Prot', None)

    gene['ensembl'] = ensembl
    gene['uniprot'] = uniprot


def query_mygene(entrez_set, tax_id):
    """Query mygene.info to get detailed gene information."""

    q_genes = entrez_set
    q_scopes = ['entrezgene', 'retired']
    output_fields = [
        'entrezgene', 'ensembl.gene', 'symbol', 'name', 'uniprot', 'taxid', 'homologene'
    ]

    mg = mygene.MyGeneInfo()
    q_results = mg.querymany(
        q_genes,
        scopes=q_scopes,
        fields=output_fields,
        returnall=True
    )

    genes_info = dict()
    homo_genes = dict()
    for gene in q_results['out']:
        q_str = gene["query"]
        if gene.get('notfound', None):  # ignore missing genes
            continue

        # If organism also matches, put the gene in `gene_info` directly
        if str(gene['taxid']) == tax_id:
            polish_gene_info(gene)
            genes_info[q_str] = {
                'mygene_id': gene.get('_id', None),
                'ncbigene': gene.get('entrezgene', None),
                'ensemblgene': gene.get('ensembl', None),
                'symbol': gene.get('symbol', None),
                'name': gene.get('name', None),
                'uniprot': gene.get('uniprot', None)
            }
            continue

        # If oragnism doesn't match, search `homologene` field
        if 'homologene' not in gene:
            continue
        for homo_tax_id, homo_gene_id in gene['homologene']['genes']:
            homo_tax_id = str(homo_tax_id)
            homo_gene_id = str(homo_gene_id)
            if homo_tax_id == tax_id:
                homo_genes[homo_gene_id] = q_str
                break

    # Search homologenes in mygene.info
    q_genes = list(homo_genes.keys())
    logging.info("Searching homologous genes")
    homo_results = mg.querymany(
        q_genes,
        scopes=q_scopes,
        fields=['entrezgene', 'ensembl.gene', 'symbol', 'name', 'uniprot'],
        species=tax_id,
        returnall=True
    )

    # Put homologene query results into `genes_info` dict too
    for gene in homo_results['out']:
        if gene.get('notfound', None):  # ignore missing genes
            continue

        polish_gene_info(gene)
        original_q_str = homo_genes[gene['query']]
        genes_info[original_q_str] = {
            'mygene_id': gene.get('_id', None),
            'ncbigene': gene.get('entrezgene', None),
            'ensemblgene': gene.get('ensembl', None),
            'symbol': gene.get('symbol', None),
            'name': gene.get('name', None),
            'uniprot': gene.get('uniprot', None)
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

            tax_id = tokens[7].strip()
            if tax_id not in organisms:
                continue

            chemical_name = tokens[0].strip()
            chemical_id = tokens[1].strip()
            gene_id = tokens[4].strip()

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
        logging.info("=" * 60)
        logging.info(f"Building '{organism_name}' genesets (taxid = {tax_id})")
        entrez_set = value['unique_genes']
        genes_info = query_mygene(entrez_set, tax_id)

        genesets = value['genesets']
        for chemical_id, ctd_info in genesets.items():
            gid_set = ctd_info['genes']
            uniq_gid = set()
            genes_found = list()
            for gid in gid_set:
                if gid not in genes_info:
                    continue
                gene = genes_info[gid]

                # Skip duplicate genes in a geneset
                mg_id = gene["mygene_id"]
                if mg_id in uniq_gid:
                    continue

                uniq_gid.add(mg_id)
                genes_found.append(gene)

            # Ignore a geneset if none of its genes is found in mygene.info
            if len(genes_found) == 0:
                continue

            # Sort `genes_found` by "mygene_id" value in each gene
            genes_found = sorted(genes_found, key=lambda x: int(x["mygene_id"]))

            chemical_name = ctd_info['chemical_name']
            cas_rn = ctd_info['cas_rn']
            my_geneset = dict()
            my_geneset['_id'] = chemical_id + "_" + tax_id
            my_geneset['is_public'] = True
            my_geneset['taxid'] = tax_id
            my_geneset['source'] = 'ctd'
            my_geneset['name'] = f"{chemical_name} interactions"
            my_geneset['description'] = f"Chemical-gene interactions of {chemical_name} in {organism_name}"
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
