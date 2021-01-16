import glob
import os

from biothings.utils.dataload import tabfile_feeder
from utils.geneset_utils import IDLookup


def load_data(data_folder):

    def get_taxid(species):
        taxids = {"Mus musculus": 10090,
                  "Bos taurus": 9913,
                  "Homo sapiens": 9606,
                  "Anopheles gambiae": 180454,
                  "Arabidopsis thaliana": 3702,
                  "Caenorhabditis elegans": 6239,
                  "Canis familiaris": 9615,
                  "Danio rerio": 7955,
                  "Drosophila melanogaster": 7227,
                  "Equus caballus": 9796,
                  "Gallus gallus": 9031,
                  "Oryza sativa": 39947,
                  "Pan troglodytes": 9598,
                  "Rattus norvegicus": 10116,
                  "Saccharomyces cerevisiae": 559292,
                  "Populus trichocarpa": 3694,
                  "Sus scrofa": 9823}
        return taxids[species]

    # Load .gmt (Gene Matrix Transposed) files
    for f in glob.glob(os.path.join(data_folder, "*.gmt")):
        # Get species name from the filename and convert to taxid
        species = f.replace(".gmt", "").split("-")[-1].replace("_", " ")
        taxid = get_taxid(species)
        print("Parsing data for {} ({})".format(species, taxid))
        # Read entire file and fetch data for joint set of all genes
        data = tabfile_feeder(f, header=0)
        all_genes = []
        for rec in data:
            all_genes += rec[2:]
        all_genes = set(all_genes)
        lookup = IDLookup(taxid)
        lookup.query_mygene(all_genes, 'entrezgene')

        # Parse each individual document
        data = tabfile_feeder(f, header=0)
        for rec in data:
            header = rec[0].split("%")
            # Get fields from header
            pathway_name = header[0]
            wikipathways_id = header[2]
            assert species == header[3], "Species does not match."
            # Get URL and gene list
            url = rec[1]
            ncbigenes = rec[2:]
            genes = []
            for g in ncbigenes:
                if lookup.query_cache.get(g):
                    genes.append(lookup.query_cache[g])

            # Format schema
            doc = {'_id': wikipathways_id,
                   'is_public': True,
                   'taxid': taxid,
                   'genes': genes,
                   'wikipathways': {
                       'id': wikipathways_id,
                       'pathway_name': pathway_name,
                       'url': url
                       }
                   }
            yield doc


if __name__ == "__main__":
    import json

    annotations = load_data("./test_data")
    with open("out.json", 'a') as outfile:
        for a in annotations:
            outfile.write(json.dumps(a, indent=2))
