import os

from biothings.utils.dataload import tabfile_feeder
from utils.geneset_utils import IDLookup


def load_data(data_folder):
    # Load .gmt (Gene Matrix Transposed) file with entrez ids
    f = os.path.join(data_folder, "ReactomePathways.gmt")
    data = tabfile_feeder(f, header=0)
    all_genes = set()
    for rec in data:
        genes = set(rec[2:])
        all_genes = all_genes | genes
    # Query gene info
    lookup = IDLookup(9606)  # Human genes
    lookup.query_mygene(all_genes, 'symbol')

    data = tabfile_feeder(f, header=0)
    for rec in data:
        name = rec[0]
        _id = rec[1]
        ncbigenes = rec[2:]
        genes = []
        for gene in ncbigenes:
            if lookup.query_cache.get(gene):
                genes.append(lookup.query_cache[gene])
        # Format schema
        doc = {'_id': _id,
               'is_public': True,
               'taxid': 9606,
               'genes': genes,
               'reactome': {
                   'id': _id,
                   'geneset_name': name,
                   }
               }
        yield doc


if __name__ == "__main__":
    import json

    annotations = load_data("./test_data")
    for a in annotations:
        print(json.dumps(a, indent=2))
