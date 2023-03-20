#!/usr/bin/env python3


def get_release(self):
    """
    Return a string that combines the release dates of both "HumanDO.obo"
    and "genemap2.txt" files.
    """

    import requests

    # Get release date of "HumanDO.obo" data file:
    obo_url = "https://raw.githubusercontent.com/DiseaseOntology/HumanDiseaseOntology/main/src/ontology/HumanDO.obo"
    obo_resp = requests.get(obo_url)
    obo_text_lines = obo_resp.text.strip("\n").split("\n")
    obo_release = ""

    # Find the line that is in the following format:
    # "data-version: doid/releases/YYYY-MM-DD/doid-non-classified.obo"
    # and extract "YYYY-MM-DD" part as release string in "HumanDO.obo":
    for line in obo_text_lines:
        if line.startswith("data-version: "):
            full_version = line.strip().split(" ")[1]
            obo_release = full_version.split("/")[2]
            break

    # Get release date of "genemap2.txt" data file:
    genemap2_url = "https://data.omim.org/downloads/V3TcgUTzQge_hC0CEPEBgA/genemap2.txt"
    genemap2_resp = requests.get(genemap2_url)
    genemap2_text_lines = genemap2_resp.text.strip("\n").split("\n")
    genemap2_release = ""

    # Find the line that is in the following format:
    # "# Genearated: YYYY-MM-DD"
    # and extract "YYYY-MM-DD" part as the release string in "genemap2.txt":
    for line in genemap2_text_lines:
        if line.startswith("# Generated: "):
            genemap2_release = line.strip().split(": ")[1]
            break

    # Return a string that combines both release dates
    return "obo-" + obo_release + "_" + "genemap2-" + genemap2_release


# Test harness
if __name__ == "__main__":
    print(get_release(None))
