import os
import bs4

import biothings, config
biothings.config_for_app(config)

from config import DATA_ARCHIVE_ROOT
from biothings.hub.dataload.dumper import HTTPDumper


class msigdbDumper(HTTPDumper):

    SRC_NAME = "msigdb"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    BASE_URL = "https://data.broadinstitute.org/gsea-msigdb/msigdb/release/"
    RELEASE_NOTES = "https://software.broadinstitute.org/cancer/software/gsea/wiki/index.php/Release_Notes"
    SCHEDULE = "0 8 20 * *"
    __metadata__ = {
        "src_meta": {
            'license_url': 'https://www.gsea-msigdb.org/gsea/msigdb_license_terms.jsp',
            'licence': 'CC Attribution 4.0 International',
            'url': 'https://www.gsea-msigdb.org/gsea/index.jsp'
            }
        }

    def get_remote_version(self):
        home = self.client.get(self.__class__.RELEASE_NOTES)
        html = bs4.BeautifulSoup(home.text, "html.parser")
        notes = html.find(id="MSigDB_Release_Notes")
        # Releases table
        table = notes.next_sibling.next_sibling.next_sibling
        assert table.name =='table', "Could not find releases table in release notes."
        # Grab first element from table
        latest = table.find_all('tr')[1]
        fields = latest.find_all('td')
        version = fields[1].contents[0]
        version = version.replace('*', '').replace('\xa0', '')
        notes_link = fields[3].find('a').get('href')
        assert notes_link.split('/')[-1].startswith('MSigDB'),\
            "Could not fetch right version number from release notes."
        return version

    def create_todump_list(self, force=False):
        self.release = self.get_remote_version()
        if force or not self.current_release or float(self.release) > float(self.current_release):
            home = self.__class__.BASE_URL
            name = "msigdb.v{}.entrez.gmt".format(self.release)
            url = home + self.release + '/' + name
            local_file = os.path.join(self.new_data_folder, name)
            self.to_dump.append({"remote": url, "local": local_file})
