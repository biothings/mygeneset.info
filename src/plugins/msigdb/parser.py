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
        # Documents have been sorted by their ORGANISM attribute using sort_genesets.xsl in post_dump() of dump.py
        current_organism = ""
        geneset_index = 0
        for line in f:
            if line.lstrip().startswith("<GENESET"):
                geneset_index += 1
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
                assert doc["taxid"] is not None, "Taxid not found. ORGANISM missing in source data: {}".format(data)
                assert doc["taxid"] != "", "Taxid not found. ORGANISM missing in source data: {}".format(data)
                # MEMBERS contains a list of genes with their original identifier, which can be any type of ID.
                # symbols contains a list of genes converted to symbols.
                # MEMBERS_EZID contains a list of gene entrez IDs, but these have been converted from their corresponding human gene.
                # MEMBERS_MAPPING contains tuples of the three above IDs.
                members =  data["MEMBERS"].split(",")
                symbols = [s.split(",")[1] for s in data["MEMBERS_MAPPING"].split("|")]
                if len(members) != len(symbols):
                    # This edge case shouldn't happen, but we can use another altnative
                    members = [s.split(",")[0] for s in data["MEMBERS_MAPPING"].split("|")]
                assert len(members) == len(symbols), "ID lists are not the same length: {} {}".format(
                    len(members), len(symbols))
                # Using symbols as the preferred id, because it consistently gives the most hits across datasets
                id_list = list(zip(symbols, members))
                if doc["taxid"] != current_organism:
                    # Start a new query cache
                    current_organism = doc["taxid"]
                    logging.info("Parsing msigdb data for organism {}".format(current_organism))
                    gene_lookup = IDLookup(doc["taxid"])
                # Figure out which scopes to use for the retry query
                original_type = data.get("CHIP")
                if original_type:
                    if original_type.endswith("GENE_SYMBOL") or original_type == "HGNC_ID":
                        scopes = 'symbol,alias'
                    elif original_type.endswith("UniProt_ID"):
                        scopes = 'uniprot'
                    elif original_type.endswith("Ensembl_Gene_ID"):
                        scopes = 'ensembl.gene'
                    elif original_type.endswith("RefSeq"):
                        scopes = 'refseq'
                    elif original_type.endswith("NCBI_Gene_ID"):
                        scopes = 'entrezgene,retired'
                    elif original_type == "UniGene_ID":
                        scopes = 'unigene'
                    else:
                        scopes = "symbol,ensembl.gene,entrezgene,uniprot,reporter,refseq,alias,unigene"
                else:
                    scopes = "symbol,ensembl.gene,entrezgene,uniprot,reporter,refseq,alias,unigene"
                # Run query
                logging.info("Queryng genes for geneset #{}: {}".format(geneset_index, doc["_id"]))
                gene_lookup.query_mygene(id_list, ['symbol,alias', scopes])
                query_results = gene_lookup.get_results(id_list)
                doc.update(query_results)  # Merge doc with query results
                # Additional msigdb data
                msigdb = {}
                msigdb["id"] = data["STANDARD_NAME"]
                msigdb["geneset_name"] = data["STANDARD_NAME"].replace("_", " ").lower()
                msigdb["systematic_name"] = data["SYSTEMATIC_NAME"]
                msigdb["category_code"] = data["CATEGORY_CODE"]
                msigdb["subcategory_code"] = data["SUB_CATEGORY_CODE"]
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
    xmlfile = os.path.join(data_folder, "msigdb_sorted.xml".format(version))
    assert os.path.exists(xmlfile), "Could not find input XML file."
    annotations = parse_msigdb(xmlfile)
    for a in annotations:
        #pass
        print(json.dumps(a, indent=2))
