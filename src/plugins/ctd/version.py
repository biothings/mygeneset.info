#!/usr/bin/env python3

# todo @Apr 2 2026 Will & Everaldo
# Human verification was added to https://ctdbase.org/about/dataStatus.go, so the version getter was failing.
# We chose a quick fix by parsing the date and size info from the FTP page to produce a unique identifier to serve as the version string.
# Future fix could include attempts to bypass the human verification check using a headless browser.


def get_release(self):
    import requests
    import re
    from datetime import datetime

    target_url = "https://ctdbase.org/reports/"
    target_file = "CTD_chem_gene_ixns.tsv.gz"

    resp = requests.get(target_url)
    resp.raise_for_status()

    match = re.search(
        rf"{re.escape(target_file)}</a>\s+(?P<day>\d{{1,2}})-(?P<month>[A-Za-z]{{3}})-(?P<year>\d{{4}})\s+\d{{2}}:\d{{2}}\s+(?P<size>\d+(?:\.\d+)?[KMGTP]?)",
        resp.text,
    )
    if match:
        parsed_date = datetime.strptime(
            f"{match.group('day')}-{match.group('month')}-{match.group('year')}",
            "%d-%b-%Y",
        )
        return (
            f"{parsed_date.strftime('%B')}-{parsed_date.day}-{parsed_date.year}-"
            f"{match.group('size')}B"
        )

    raise ValueError(f"Could not find {target_file} on {target_url}")


## deprecated version getter, left here for reference

# def get_release(self):
#     import requests
#     from lxml import html
#
#     release = ""
#
#     data_status_url = "https://ctdbase.org/about/dataStatus.go"
#     resp = requests.get(data_status_url)
#     tree = html.fromstring(resp.content)
#
#     status_text = tree.xpath('//div[@id="sitelegal"]/a/text()')
#     if len(status_text) >= 2:
#         # Split release date into three parts
#         release_tokens = status_text[-2].strip().replace(",", "").split()
#         # Add revision number
#         release_tokens.append(status_text[-1].strip())
#         # Combine date and revision number together
#         release = "-".join(release_tokens)
#
#     return release


# Test harness
if __name__ == "__main__":
    print(get_release(None))
