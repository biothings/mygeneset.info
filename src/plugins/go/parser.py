import glob
import json
import os
import sys

sys.path.append("../../")
from biothings.utils.dataload import tabfile_feeder, dict_sweep, unlist
from utils.geneset_utils import IDLookup


def load_data(data_folder):
    # Ontology data
    go_file = os.path.join(data_folder, "go.json")
    goterms = parse_ontology(go_file)
    # Gene annotation files
    for f in glob.glob(os.path.join(data_folder, "*.gaf.gz")):
        print("Parsing {}".format(f))
        docs = parse_gene_annotations(f)

        # Create gene ID cache. Join all gene sets and fetch ids.
        all_genes = set()
        for _id, annotations in docs.items():
            for key in ["genes", "excluded_genes", "contributing_genes",
                        "colocalized_genes"]:
                if annotations.get(key) is not None:
                    all_genes = all_genes | annotations[key]
        uniprot = [i for i, j in all_genes]
        symbols = [j for i, j in all_genes]
        taxid = annotations['taxid']
        # Fetch gene data from mygene.info
        lookup = IDLookup(taxid)
        lookup.query_mygene(uniprot, "uniprot,retired,accession")
        lookup.retry_failed_with_new_ids(symbols, "symbol")

        for _id, annotations in docs.items():
            # Add ontology annotations
            annotations['go'] = goterms[_id]
            annotations['source'] = 'go'
            annotations['name'] = annotations['go'].pop('name')
            annotations['description'] = annotations['go'].pop('description')
            # Add gene sets
            if annotations.get("genes") is not None:
                new_genes = []
                for u, s in annotations['genes']:
                    if lookup.query_cache.get(u) is not None:
                        new_genes.append(lookup.query_cache[u])
                    elif lookup.query_cache.get(s) is not None:
                        new_genes.append(lookup.query_cache[s])
                annotations['genes'] = new_genes
            else:
                # No genes in set
                continue

            for key in ["excluded_genes", "contributing_genes",
                        "colocalized_genes"]:
                if annotations.get(key) is not None:
                    new_genes = []
                    for u, s in annotations.pop(key):
                        if lookup.query_cache.get(u) is not None:
                            new_genes.append(lookup.query_cache[u])
                        elif lookup.query_cache.get(s) is not None:
                            new_genes.append(lookup.query_cache[s])
                    annotations['go'][key] = new_genes
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
                taxid = int(rec[12].split("|")[0].replace("taxon:", ""))
                genesets[_id] = {"_id":  _id + "_" + str(taxid),
                                 "is_public": True,
                                 "taxid": taxid}
            uniprot = rec[1]
            symbol = rec[2]
            qualifiers = rec[3].split("|")
            # The gene can belong to several sets:
            if "NOT" in qualifiers:
                # Genes similar to genes in go term, but should be excluded
                genesets[_id].setdefault("excluded_genes", set()).add(
                        (uniprot, symbol))
            if "contributes_to" in qualifiers:
                # Genes that contribute to the specified go term
                genesets[_id].setdefault("contributing_genes", set()).add(
                        (uniprot, symbol))
            if "colocalizes_with" in qualifiers:
                # Genes colocalized with specified go term
                genesets[_id].setdefault("colocalized_genes", set()).add(
                        (uniprot, symbol))
            else:
                # Default set: genes that belong to go term
                genesets[_id].setdefault("genes", set()).add(
                        (uniprot, symbol))
    return genesets


def parse_ontology(f):
    "Get GO-term metadata from ontology JSON dump."
    with open(f, 'r') as infile:
        data = json.load(infile)
    nodes = data['graphs'][0]['nodes']
    go_terms = {}
    for node in nodes:
        url = node['id']
        _id = url.split("/")[-1]
        if not _id.startswith("GO_"):
            continue
        go_terms[_id] = {"id": _id.replace("_", ":"),
                         "url": url,}
        properties = node['meta'].get('basicPropertyValues')
        for p in properties:
            if p['val'] in ["biological_process", "cellular_component", "molecular_function"]:
                go_terms[_id]["class"] = [p['val']]
        if node.get('lbl'):
            go_terms[_id]['name'] = node['lbl']
        if node['meta'].get("definition"):
            go_terms[_id]['description'] = node['meta']['definition'].get('val')
            go_terms[_id]['xrefs'] = node['meta']['definition'].get('xrefs')
    go_terms = unlist(go_terms)
    go_terms = dict_sweep(go_terms)
    return go_terms


if __name__ == "__main__":
    import os
    annotations = load_data("./test_data")
    with open("out.json", 'a') as outfile:
        for a in annotations:
            outfile.write(json.dumps(a, indent=2))
