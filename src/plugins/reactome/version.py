def get_release(self):
    import requests

    resp = requests.get("https://reactome.org/ContentService/data/database/version")
    if resp.status_code == 200:
        return str(resp.json())
