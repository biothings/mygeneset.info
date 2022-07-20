import os
from glob import glob

if __name__ == "__main__":
    import sys
    sys.path.append("../../")

import biothings_client
import pandas as pd
from biothings.utils.dataload import dict_sweep
from utils.geneset_utils import IDLookup


def load_data(data_folder):
    genesets = parse_genes(data_folder)
    chemsets = parse_metabolites(data_folder)
    f = os.path.join(data_folder, "smpdb_pathways.csv")
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
                   'geneset_name': data['Name'][i],
                   'pw_id': data['PW ID'][i],
                   'pathway_subject': data['Subject'][i],
                   }
               }
        if genesets.get(smpdb_id):
            doc.update(genesets[smpdb_id])
        if chemsets.get(smpdb_id):
            doc['metabolites'] = chemsets[smpdb_id]
        if doc.get('metabolites') or doc.get('genes'):
            doc = dict_sweep(doc, vals=[',', None])
            yield doc


def parse_genes(data_folder):
    # Concatenate all unique genes in csv files and query gene information.
    all_genes = set()
    fields = ['Uniprot ID', 'Gene Name']
    for f in glob(os.path.join(data_folder, "*_proteins.csv")):
        tmp_df = pd.read_csv(f, usecols=fields).fillna("")
        # Skip empty files
        if len(tmp_df) == 0:
            continue
        all_genes = all_genes | set(zip(tmp_df['Uniprot ID'], tmp_df['Gene Name']))
    all_genes = list(all_genes)
    gene_lookup = IDLookup(9606)
    gene_lookup.query_mygene(all_genes, ['uniprot', 'symbol,alias'])

    # Every file contains a separate geneset
    # We must open each file again and add the genes to the correct set
    gene_sets = {}
    fields = ['SMPDB ID', 'Uniprot ID', 'Gene Name', 'GenBank ID', 'Locus']
    for f in glob(os.path.join(data_folder, "*_proteins.csv")):
        data = pd.read_csv(f, usecols=fields).fillna("")
        if len(data) == 0:
            continue
        smpdb_id = data['SMPDB ID'][0]
        genes = list(zip(data['Uniprot ID'], data['Gene Name']))
        gene_sets[smpdb_id] = gene_lookup.get_results(genes)
    return gene_sets


def parse_metabolites(data_folder):
    all_compounds = set()
    fields = ['InChI Key']
    for f in glob(os.path.join(data_folder, "*_metabolites.csv")):
        tmp_df = pd.read_csv(f, usecols=fields).fillna("")
        # Skip empty files
        if len(tmp_df) == 0:
            continue
        all_compounds = all_compounds | set(tmp_df['InChI Key'])
    # Query MyChem.info
    mc = biothings_client.MyChemInfo()
    resp = mc.getchems(all_compounds, fields='pubchem.cid,chembl.molecule_chembl_id', dotfield=True)
    results = {}
    not_found = []
    for r in resp:
        if r.get('notfound'):
            not_found.append(r)
        else:
            results[r['query']] = r
    if len(not_found) > 0:
        print("{} input query terms found no hit: {}".format(
            len(not_found), not_found))

    metabolite_sets = {}
    for f in glob(os.path.join(data_folder, "*_metabolites.csv")):
        data = pd.read_csv(f).fillna("")
        # Skip empty files
        if len(data) == 0:
            continue
        # Columns from dataframe
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

        metabolites = []
        for i in range(len(data)):
            query_results = results.get(inchikey[i])
            if query_results:
                mychemid = query_results['_id']
                pubchem_id = query_results.get('pubchem.cid')
                chembl_id = query_results.get('chembl.molecule_chembl_id')
            else:
                # Chemical not found in MyChem.info
                continue

            metabolites.append(
                    {'mychem_id': mychemid,
                     'smpdb_metabolite': pw_id[i],
                     'name': metabolite_name[i],
                     'hmdb': hmdb[i],
                     'kegg_cid': kegg[i],
                     'chebi': str(chebi[i]),
                     'drugbank': drugbank[i],
                     'smiles': smiles[i],
                     'iupac': iupac[i],
                     'cas': cas[i],
                     'inchi': inchi[i],
                     'inchikey': inchikey[i],
                     'pubchem': pubchem_id,
                     'chembl': chembl_id
                     })
        metabolite_sets[smpdb_id] = metabolites
    return metabolite_sets


if __name__ == "__main__":
    import json

    annotations = load_data("./test_data")
    for a in annotations:
        #pass
        print(json.dumps(a, indent=2))
