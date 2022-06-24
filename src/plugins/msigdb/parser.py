import logging
import os
import xml.etree.ElementTree as ET

# Some imports for running parser locally
if __name__ == "__main__":
    import json
    import sys

    sys.path.append("../../")
    sys.path.append("../../../../")

    import config
    from dump import msigdbDumper

from biothings.utils.dataload import dict_sweep
from utils.geneset_utils import IDLookup


def parse_msigdb(data_file):
    TAXIDS = {
        "Homo sapiens": 9606,
        "Mus musculus": 10090,
        "Rattus norvegicus": 10116,
        "Macaca mulatta": 9544,
        "Danio rerio": 7955
    }
    with open(data_file, 'r') as f:
        # File contains newline-delimited XML documents.
        # Each document is a single gene set.
        for line in f:
            if line.startswith("<GENESET"):
                doc = {}
                tree = ET.fromstring(line)
                assert tree.tag == "GENESET", "Expected GENESET tag"
                data = tree.attrib
                doc["_id"] = data["STANDARD_NAME"]
                doc["name"] = data["STANDARD_NAME"].replace("_", " ").lower()
                doc["description"] = data["DESCRIPTION_BRIEF"]
                doc["taxid"] = TAXIDS[data.get("ORGANISM")]
                doc["source"] = "msigdb"
                doc["is_public"] = True
                assert doc["taxid"] is not None, "Taxid not found. ORGANISM missing is source data: {}".format(data)
                assert doc["taxid"] != "", "Taxid not found. ORGANISM missing is source data: {}".format(data)
                # Look up gene IDs.DESCRIPTION_BRIEF Genes are stored in four different attributes in the data file:
                # 1) MEMBERS contains a list of genes with their original identifier, which can be any type of ID.
                # 2) MEMBERS_SYMBOLIZED contains a list of genes converted to symbols.
                # 3) MEMBERS_EZID contains a list of gene entrez IDs, but these have been converted from their corresponding human gene.
                # 4) MEMBERS_MAPPING contains tuples of the three above IDs.
                # We will use MEMBERS_MAPPNG to extract MEMBERS as the prefered id for lookup, followed by MEMBERS_SYMBOLIZED as backup.
                members = [mapping.split(",")[0] for mapping in data["MEMBERS_MAPPING"].split("|")]
                members_symbolized = [mapping.split(",")[1] for mapping in data["MEMBERS_MAPPING"].split("|")]
                gene_lookup = IDLookup(doc["taxid"])
                gene_lookup.query_mygene(members, "symbol,ensembl.gene,entrezgene,uniprot,reporter,refseq,alias")
                gene_lookup.retry_failed_with_new_ids(members, "all")
                genes = []
                for i, j in zip(members, members_symbolized):
                    if gene_lookup.query_cache.get(i) is not None:
                        genes += gene_lookup.query_cache[i]
                    elif gene_lookup.query_cache.get(j) is not None:
                        genes += gene_lookup.query_cache[j]
                    else:
                        logging.info("Could not find gene {} with taxid {}".format(i, doc["taxid"]))
                doc["genes"] = genes
                # Additional msigdb data
                msigdb = {}
                msigdb["id"] = data["STANDARD_NAME"]
                msigdb["geneset_name"] = data["STANDARD_NAME"].replace("_", " ").lower()
                msigdb["category_code"] = data["CATEGORY_CODE"]
                msigdb["subcategory_code"] = data["SUB_CATEGORY_CODE"]
                msigdb["authors"] = data.get("AUTHORS").split(",")
                msigdb["contributor"] = data.get("CONTRIBUTOR")
                msigdb["contributor_org"] = data.get("CONTRIBUTOR_ORG")
                msigdb["source"]= data.get("EXACT_SOURCE")
                msigdb["abstract"] = data.get("DESCRIPTION_FULL")
                msigdb["pmid"] = data.get("PMID")
                msigdb["geo_id"] = data.get("GEOID")
                msigdb["tags"] = data.get("TAGS")
                msigdb["url"] = {
                    "external_details": data.get("EXTERNAL_DETAILS_URL"),
                    "geneset_listing": data.get("GENESET_LISTING_URL")
                }
                doc["msigdb"] = msigdb
                # Clean up empty fields
                doc = dict_sweep(doc)
                yield doc


if __name__ == "__main__":
    dumper = msigdbDumper()
    version = dumper.get_remote_version()
    data_folder = os.path.join(config.DATA_ARCHIVE_ROOT, "msigdb", version)
    xmlfile = os.path.join(data_folder, "msigdb_v{}.xml".format(version))
    annotations = parse_msigdb(xmlfile)
    for a in annotations:
        pass
        #print(json.dumps(a, indent=2))
