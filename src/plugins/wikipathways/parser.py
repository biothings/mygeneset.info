import glob
import os
import logging

from biothings.utils.dataload import tabfile_feeder

if __name__ == "__main__":
    import sys

    sys.path.append("../../")

from utils.mygene_lookup import MyGeneLookup


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
                  "Solanum lycopersicum": 4081,
                  "Rattus norvegicus": 10116,
                  "Saccharomyces cerevisiae": 559292,
                  "Populus trichocarpa": 3694,
                  "Sus scrofa": 9823}
        if species in taxids:
            return taxids[species]
        else:
            logging.error("Taxid not found for species {}".format(species))

    # Load .gmt (Gene Matrix Transposed) files
    for f in glob.glob(os.path.join(data_folder, "*.gmt")):
        # Get species name from the filename and convert to taxid
        species = f.replace(".gmt", "").split("-")[-1].replace("_", " ")
        taxid = get_taxid(species)
        logging.info("Parsing data for {} ({})".format(species, taxid))
        # Read entire file and fetch data for joint set of all genes
        data = tabfile_feeder(f, header=0)
        all_genes = []
        for rec in data:
            all_genes += rec[2:]
        all_genes = set(all_genes)
        gene_lookup = MyGeneLookup(taxid)
        gene_lookup.query_mygene(all_genes, 'entrezgene,retired')

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
            # Format document
            doc = {'_id': wikipathways_id,
                   'name': pathway_name,
                   'is_public': True,
                   'taxid': taxid,
                   'source': 'wikipathways',
                   'wikipathways': {
                       'id': wikipathways_id,
                       'pathway_name': pathway_name,
                       'url': url
                       }
                   }
            # Get gene objects from lookup
            lookup_results = gene_lookup.get_results(ncbigenes)
            doc.update(lookup_results)
            yield doc


if __name__ == "__main__":
    import json

    annotations = load_data("./test_data")
    for a in annotations:
        # pass
        print(json.dumps(a, indent=2))
