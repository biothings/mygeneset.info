import os

import biothings
import bs4
import config

biothings.config_for_app(config)

from biothings.hub.dataload.dumper import HTTPDumper
from config import DATA_ARCHIVE_ROOT


class msigdbDumper(HTTPDumper):
    SRC_NAME = "msigdb"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    BASE_URL = "https://data.broadinstitute.org/gsea-msigdb/msigdb/release/"
    HOMEPAGE = "http://www.gsea-msigdb.org/gsea/msigdb/index.jsp"
    SCHEDULE = "0 8 20 * *"
    __metadata__ = {
        "src_meta": {
            'license_url': 'https://www.gsea-msigdb.org/gsea/msigdb_license_terms.jsp',
            'licence': 'CC Attribution 4.0 International',
            'url': 'https://www.gsea-msigdb.org/gsea/index.jsp'
            }
        }

    def get_remote_version(self):
        """Scrape version number from MSIGDB homepage.
        Header 1 text ends with the version number.
        """
        home = self.client.get(self.__class__.HOMEPAGE)
        html = bs4.BeautifulSoup(home.text, "html.parser")
        header = html.find("h1", {"class": "msigdbhome"})
        version = header.text.split(" ")[-1]
        assert version.startswith("v"),\
            "Could not parse version number from HTML field."
        version = version[1:]
        return version

    def create_todump_list(self, force=False):
        """Dump XML geneset file."""
        self.release = self.get_remote_version()
        if force or not self.current_release or float(self.release) > float(self.current_release):
            home = self.__class__.BASE_URL
            name = "msigdb_v{}.xml".format(self.release)
            url = home + self.release + '/' + name
            local_file = os.path.join(self.new_data_folder, name)
            self.to_dump.append({"remote": url, "local": local_file})
