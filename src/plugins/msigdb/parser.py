import logging
import os

import lxml.etree as ET

# Some imports for running parser from file
if __name__ == "__main__":
    import json
    import sys

    sys.path.append("../../")
    sys.path.append("../../../../")

    import config
    from dump import msigdbDumper

from biothings.utils.dataload import dict_sweep, unlist
from utils.mygene_lookup import MyGeneLookup
from xml_encoder import xmlEncoder


def parse_msigdb(data_folder):
    """
    The XML data provides original gene ids, as well as orthology-converted ones.
    This parser currently uses the organism taxid of the original (upstream and pre-ortholog conversion) identifiers
    for lookup and to assign the geneset taxid.

    This means that even though the downloaded dataset is a "mouse" or "human" collection, genesets will be ingested
    as several different organism such as human, mouse, rat, rhesus monkey, and zebrafish.

    To prevent confusion, we add an msigdb-specific metadata field 'dataset' to keep track of whether the geneset
    originated from the "human" or "mouse" dataset.
    """

    TAXIDS = {
        "Homo sapiens": 9606,
        "Mus musculus": 10090,
        "Rattus norvegicus": 10116,
        "Macaca mulatta": 9544,
        "Danio rerio": 7955,
    }
    # Basic category codes from msigdb, human codes prepend "C" and mouse codes prepend "M" to the given number
    CATEGORY_CODES = {
        "H": "hallmark genesets",
        "1": "positional genesets",
        "2": "curated genesets",
        "3": "regulatory genesets",
        "4": "computational genesets",
        "5": "ontology genesets",
        "6": "oncogenic signature genesets",
        "7": "immunologic signature genesets",
        "8": "cell type signature genesets",
    }

    # Decode special characters
    encoder = xmlEncoder()

    for f in ["human_genesets.xml"]:
        data_file = os.path.join(data_folder, f)
        # File contains newline-delimited XML documents. Each document is a single geneset.
        # Documents have been sorted by their ORGANISM attribute using sort_genesets.xsl in post_dump() of dump.py
        with open(data_file, "r") as f:
            current_organism = ""
            geneset_index = 0  # Keep track of current line for logging/debugging purposes
            for line in f:
                if line.lstrip().startswith("<GENESET"):
                    geneset_index += 1
                    doc = {}
                    line = line.replace("&quot;", "")  # Some lines have random html quote codes
                    tree = ET.fromstring(line)
                    assert tree.tag == "GENESET", "Expected GENESET tag"
                    data = tree.attrib
                    logging.info("Uploading _id: {}".format(data["STANDARD_NAME"]))
                    doc["_id"] = data["STANDARD_NAME"]
                    doc["name"] = data["STANDARD_NAME"].replace("_", " ").lower()
                    doc["description"] = data["DESCRIPTION_BRIEF"]
                    doc["taxid"] = TAXIDS[data.get("ORGANISM")]
                    doc["source"] = "msigdb"
                    doc["is_public"] = True
                    assert (
                        doc["taxid"] is not None
                    ), "Taxid not found. ORGANISM missing in source data: {}".format(data)
                    assert (
                        doc["taxid"] != ""
                    ), "Taxid not found. ORGANISM missing in source data: {}".format(data)
                    # Start a gene query
                    if doc["taxid"] != current_organism:
                        current_organism = doc["taxid"]
                        logging.info(
                            "Parsing msigdb data for organism {}".format(current_organism)
                        )
                        gene_lookup = MyGeneLookup(doc["taxid"])
                    # MEMBERS contains a "," delimited list of genes with their original identifier.
                    # MEMBERS_SYMBOLIZED contains a "," delimited list of genes converted to symbols (but sometimes contains other types of ids).
                    # MEMBERS_EZID contains a "," delimited list of entrez IDs, but these have been converted from their corresponding human gene.
                    # MEMBERS_MAPPING contains "|" delimited "," delimited tuples of the three above IDs.
                    # Figure out which scopes to use for the MEMBERS set
                    original_type = data.get("CHIP")
                    if original_type:
                        if original_type.endswith("GENE_SYMBOL") or original_type == "HGNC_ID":
                            members_scopes = "symbol,alias"
                        elif original_type.endswith("UniProt_ID"):
                            members_scopes = "uniprot"
                        elif original_type.endswith("Ensembl_Gene_ID"):
                            members_scopes = "ensembl.gene"
                        elif original_type.endswith("RefSeq"):
                            members_scopes = "refseq"
                        elif original_type.endswith("NCBI_Gene_ID"):
                            members_scopes = "entrezgene,retired"
                        elif original_type == "UniGene_ID":
                            members_scopes = "unigene"
                        else:
                            # default to all
                            members_scopes = "symbol,ensembl.gene,entrezgene,uniprot,reporter,refseq,alias,unigene"
                    else:
                        members_scopes = (
                            "symbol,ensembl.gene,entrezgene,uniprot,reporter,refseq,alias,unigene"
                        )
                    if "|" in data["MEMBERS"]:
                        # Sometimes ids contain a "|" with a prefix like 'ens', or 'linc'
                        # to indicate the id type is different from the rest.
                        # We can't use this to determine the scope, so we'll just use the default.
                        members_scopes = (
                            "symbol,ensembl.gene,entrezgene,uniprot,reporter,refseq,alias,unigene"
                        )
                    # Prepare list of genes to query. We will query gene symbols and original ids.
                    members_mapping = [
                        s.split(",")
                        for s in data["MEMBERS_MAPPING"].split("|")
                        if len(s.split(",")) == 3
                    ]
                    symbols = []
                    for id_tuple in members_mapping:
                        if id_tuple[1] == "":
                            symbols.append(id_tuple[0])  # If no symbol, use the original ID
                        else:
                            symbols.append(id_tuple[1])
                    members_raw = data["MEMBERS"].split(",")
                    members = []
                    for m in members_raw:
                        if "|" in m:
                            # Remove prefixes like 'ens' or 'linc'
                            members.append(m.split("|")[1])
                        else:
                            members.append(m)
                    if len(members) != len(symbols):
                        # This edge case shouldn't happen, but we can use another altnative
                        members = [
                            s.split(",")[0]
                            for s in data["MEMBERS_MAPPING"].split("|")
                            if len(s.split(",")) == 3
                        ]
                    assert len(members) == len(
                        symbols
                    ), "ID lists are not the same length: {} {}".format(len(members), len(symbols))
                    # Using symbols as the preferred id, because it consistently gives the most hits across datasets
                    id_list = list(zip(symbols, members))
                    # Run query
                    logging.info(
                        "Querying genes for geneset #{}: {}".format(geneset_index, doc["_id"])
                    )
                    gene_lookup.query_mygene(id_list, ["symbol,alias", members_scopes])
                    query_results = gene_lookup.get_results(id_list)
                    doc.update(query_results)  # Merge doc with query results
                    # Additional msigdb data
                    msigdb = {}
                    msigdb["id"] = data["STANDARD_NAME"]
                    msigdb["geneset_name"] = data["STANDARD_NAME"].replace("_", " ").lower()
                    msigdb["systematic_name"] = data["SYSTEMATIC_NAME"]
                    msigdb["category"] = {}
                    msigdb["category"]["code"] = data["CATEGORY_CODE"]
                    msigdb["category"]["name"] = CATEGORY_CODES.get(data["CATEGORY_CODE"][-1])
                    msigdb["subcategory"] = {}
                    msigdb["subcategory"]["code"] = data["SUB_CATEGORY_CODE"]
                    msigdb["authors"] = data.get("AUTHORS").split(",")
                    msigdb["contributor"] = data.get("CONTRIBUTOR")
                    msigdb["contributor_org"] = data.get("CONTRIBUTOR_ORG")
                    msigdb["source"] = data.get("EXACT_SOURCE")
                    msigdb["source_identifier"] = original_type
                    msigdb["abstract"] = data.get("DESCRIPTION_FULL")
                    msigdb["pmid"] = data.get("PMID")
                    msigdb["geo_id"] = data.get("GEOID")
                    msigdb["tags"] = data.get("TAGS")
                    msigdb["url"] = {
                        "external_details": data.get("EXTERNAL_DETAILS_URL"),
                        "geneset_listing": data.get("GENESET_LISTING_URL"),
                    }

                    # Replace &amp; by space in all fields of msigdb
                    for key, value in msigdb.items():
                        if isinstance(value, str):
                            msigdb[key] = encoder.decode_xml(value)

                    doc["msigdb"] = msigdb
                    # Remove lists with only one item
                    doc = unlist(doc)
                    # Clean up empty fields
                    doc = dict_sweep(doc, vals=[None])
                    yield doc


if __name__ == "__main__":
    dumper = msigdbDumper()
    version = dumper.get_remote_version()
    data_folder = os.path.join(config.DATA_ARCHIVE_ROOT, "msigdb", version)
    annotations = parse_msigdb(data_folder)
    for a in annotations:
        # pass
        print(json.dumps(a, indent=2))
