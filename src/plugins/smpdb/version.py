def get_release(self):
    import requests
    import datetime

    data_urls = ["https://smpdb.ca/downloads/smpdb_pathways.csv.zip",
                 "https://smpdb.ca/downloads/smpdb_metabolites.csv.zip",
                 "https://smpdb.ca/downloads/smpdb_proteins.csv.zip"]
    latest_update = datetime.datetime.min
    for url in data_urls:
        resp = requests.head(url)
        if resp.status_code == 200:
            date = resp.headers['Last-Modified']
            date = datetime.datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %Z')
            if date > latest_update:
                latest_update = date
            return latest_update.strftime('%m-%d-%Y')
