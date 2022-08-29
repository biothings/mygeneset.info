import os

from biothings.utils.dataload import tabfile_feeder

if __name__ == "__main__":
    import sys

    sys.path.append("../../")

from utils.mygene_lookup import MyGeneLookup


def load_data(data_folder):
    # Load .gmt (Gene Matrix Transposed) file with entrez ids
    f = os.path.join(data_folder, "ReactomePathways.gmt")
    data = tabfile_feeder(f, header=0)
    all_genes = set()
    for rec in data:
        genes = set(rec[2:])
        all_genes = all_genes | genes
    # Query gene info
    gene_lookup = MyGeneLookup(9606)  # Human genes
    gene_lookup.query_mygene(all_genes, 'symbol,alias')

    data = tabfile_feeder(f, header=0)
    for rec in data:
        name = rec[0]
        _id = rec[1]
        ncbigenes = rec[2:]
        lookup_results = gene_lookup.get_results(ncbigenes)
        # Format schema
        doc = {'_id': _id,
               'name': name,
               'is_public': True,
               'taxid': 9606,
               'source': 'reactome',
               'reactome': {
                   'id': _id,
                   'geneset_name': name,
                   }
               }
        doc.update(lookup_results)
        yield doc


if __name__ == "__main__":
    import json

    annotations = load_data("./test_data")
    for a in annotations:
        print(json.dumps(a, indent=2))
