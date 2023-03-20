import glob
import json
import logging
import os
import sys

sys.path.append("../../")
from biothings.utils.dataload import dict_sweep, tabfile_feeder, unlist
from utils.mygene_lookup import MyGeneLookup


def load_data(data_folder):
    # Ontology data
    go_file = os.path.join(data_folder, "go.json")
    goterms = parse_ontology(go_file)
    # Gene annotation files
    for f in glob.glob(os.path.join(data_folder, "*.gaf.gz")):
        logging.info("Parsing {}".format(f))
        docs = parse_gene_annotations(f)

        # Create a set of all gene-related annotations
        # Each gene is a tuple (uniprot, symbol)
        all_genes = set()
        for _id, annotations in docs.items():
            for key in ["genes", "excluded", "contributing", "colocalized"]:
                if annotations.get(key) is not None:
                    all_genes = all_genes | annotations[key]
        taxid = annotations["taxid"]
        # Fetch gene data from mygene.info
        lookup = MyGeneLookup(taxid)
        lookup.query_mygene(list(all_genes), ["uniprot,retired,accession", "symbol,alias"])

        for _id, annotations in docs.items():
            # Add ontology annotations
            annotations["go"] = goterms[_id]
            annotations["source"] = "go"
            # Add gene sets
            if annotations.get("genes") is not None:
                annotations["name"] = annotations["go"]["name"]
                annotations["description"] = annotations["go"]["description"]
                # Add gene lookup data
                annotations.update(lookup.get_results(list(annotations["genes"])))
            else:
                # No genes in set
                continue

            # TODO: I don't quite like how this data is structured.
            # It might be better to create sepparate genesets with different _id and names
            # for example: "GO_XXXXX_TAXID_excluded" and "GO_XXXXX_TAXID_contributing"
            for key in ["excluded", "contributing", "colocalized"]:
                if annotations.get(key) is not None:
                    annotations["go"][key] = lookup.get_results(list(annotations.pop(key)))
            # Clean up data
            annotations = unlist(annotations)
            annotations = dict_sweep(annotations)
            yield annotations


def parse_gene_annotations(f):
    """Parse a gene annotation (.gaf.gz) file."""
    data = tabfile_feeder(f, header=0)
    genesets = {}
    for rec in data:
        if not rec[0].startswith("!"):
            _id = rec[4].replace(":", "_")
            if genesets.get(_id) is None:
                taxid = str(rec[12].split("|")[0].replace("taxon:", ""))
                genesets[_id] = {"_id": _id + "_" + str(taxid), "is_public": True, "taxid": taxid}
            uniprot = rec[1]
            symbol = rec[2]
            qualifiers = rec[3].split("|")
            # The gene can belong to several sets:
            if "NOT" in qualifiers:
                # Genes similar to genes in go term, but should be excluded
                genesets[_id].setdefault("excluded", set()).add((uniprot, symbol))
            if "contributes_to" in qualifiers:
                # Genes that contribute to the specified go term
                genesets[_id].setdefault("contributing", set()).add((uniprot, symbol))
            if "colocalizes_with" in qualifiers:
                # Genes colocalized with specified go term
                genesets[_id].setdefault("colocalized", set()).add((uniprot, symbol))
            else:
                # Default set: genes that belong to go term
                genesets[_id].setdefault("genes", set()).add((uniprot, symbol))
    return genesets


def parse_ontology(f):
    "Get GO-term metadata from ontology JSON dump."
    with open(f, "r") as infile:
        data = json.load(infile)
    nodes = data["graphs"][0]["nodes"]
    go_terms = {}
    for node in nodes:
        url = node["id"]
        _id = url.split("/")[-1]
        if not _id.startswith("GO_"):
            continue
        go_terms[_id] = {"id": _id.replace("GO_", "GO:"), "url": url}  # Convert to CURIE format
        properties = node["meta"].get("basicPropertyValues")
        for p in properties:
            if p["val"] in ["biological_process", "cellular_component", "molecular_function"]:
                go_terms[_id]["class"] = [p["val"]]
        if node.get("lbl"):
            go_terms[_id]["name"] = node["lbl"]
        if node["meta"].get("definition"):
            go_terms[_id]["description"] = node["meta"]["definition"].get("val")
            go_terms[_id]["xrefs"] = node["meta"]["definition"].get("xrefs")
    go_terms = unlist(go_terms)
    go_terms = dict_sweep(go_terms)
    return go_terms


if __name__ == "__main__":
    annotations = load_data("./test_data")

    for a in annotations:
        print(json.dumps(a, indent=2))
