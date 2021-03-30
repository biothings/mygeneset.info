import os
from glob import glob

import sys
sys.path.append("../../")

import pandas as pd
from utils.geneset_utils import IDLookup


def load_data(data_folder):
    # Parse pathway metadata
    f = os.path.join(data_folder, "smpdb_pathways.csv")
    metabolitesets = parse_metabolites(data_folder) genesets = parse_genes(data_folder)
    data = pd.read_csv(f, quotechar='"')
    for i in range(len(data)):
        smpdb_id = data['SMPDB ID'][i]
        doc = {'_id': smpdb_id,
               'name': data['Name'][i],
               'description': data['Description'][i],
               'source': 'smpdb',
               'taxid': 9606,
               'smpdb': {
                   'id': smpdb_id,
                   'pw_id': data['PW ID'][i],
                   'pathway_subject': data['Subject'][i],
                   }
               }
        if genesets.get(smpdb_id):
            doc['genes'] = genesets[smpdb_id]
        if metabolitesets.get(smpdb_id):
            doc['metabolites'] = metabolitesets[smpdb_id]
        if doc.get('metabolites') or doc.get('genes'):
            yield doc


def parse_genes(data_folder):
    gene_sets = {}
    gene_cache = {}
    gene_lookup = IDLookup(9606, cache_dict=gene_cache)
    for f in glob(os.path.join(data_folder, "*_proteins.csv")):
        fields = ['SMPDB ID', 'Uniprot ID', 'Gene Name', 'GenBank ID', 'Locus']
        data = pd.read_csv(f, usecols=fields)
        # Query gene info
        gene_lookup.query_mygene(data['Uniprot ID'], 'uniprot')
        gene_lookup.retry_failed_with_new_ids(data['Gene Name'], 'symbol')

        smpdb_id = data['SMPDB ID'][0]
        genes = []
        for gene in data['Uniprot ID']:
            if gene_lookup.query_cache.get(gene):
                genes.append(gene_lookup.query_cache[gene])
        for gene in data['Gene Name']:
            if gene_lookup.query_cache.get(gene):
                genes.append(gene_lookup.query_cache[gene])
        gene_sets[smpdb_id] = genes
    return gene_sets


def parse_metabolites(data_folder):
    metabolite_sets = {}
    for f in glob(os.path.join(data_folder, "*_metabolites.csv")):
        data = pd.read_csv(f)
        smpdb_id = data['SMPDB ID'][0]

        pw_id = data['Metabolite ID']
        metabolite_name = data['Metabolite Name']
        hmdb = data['HMDB ID']
        kegg = data['KEGG ID']
        chebi = data['ChEBI ID']
        drugbank = data['DrugBank ID']
        cas = data['CAS']
        iupac = data['IUPAC']
        smiles = data['SMILES']
        inchi = data['InChI']
        inchikey = data['InChI Key']

        metabolites = [
                {'pw_id': pw_id[i],
                 'name': metabolite_name[i],
                 'hmdb': hmdb[i],
                 'kegg': kegg[i],
                 'chebi': str(chebi[i]),
                 'drugbank': drugbank[i],
                 'smiles': smiles[i],
                 'iupac': iupac[i],
                 'cas': cas[i],
                 'inchi': inchi[i],
                 'inchikey': inchikey[i]
                 } for i in range(len(data))]
        metabolite_sets[smpdb_id] = metabolites
    return metabolite_sets


if __name__ == "__main__":
    import json

    annotations = load_data("./test_data")
    for a in annotations:
        print(json.dumps(a, indent=2))
