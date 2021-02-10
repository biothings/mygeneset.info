#!/usr/bin/env python3


def get_release(self):
    import requests
    from lxml import html

    release = ""

    data_status_url = "https://ctdbase.org/about/dataStatus.go"
    resp = requests.get(data_status_url)
    tree = html.fromstring(resp.content)

    status_text = tree.xpath('//div[@id="sitelegal"]/a/text()')
    if len(status_text) >= 2:
        # Split release date into three parts
        release_tokens = status_text[-2].strip().replace(',', '').split()
        # Add revision number
        release_tokens.append(status_text[-1].strip())
        # Combine date and revision number together
        release = "-".join(release_tokens)

    return release


# Test harness
if __name__ == "__main__":
    print(get_release(None))
