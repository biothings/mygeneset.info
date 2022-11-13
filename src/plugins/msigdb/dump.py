import glob
import logging
import os

import biothings
import bs4
import config
import lxml.etree as ET

biothings.config_for_app(config)

from biothings.hub.dataload.dumper import HTTPDumper
from biothings.utils.common import unzipall
from config import DATA_ARCHIVE_ROOT


class msigdbDumper(HTTPDumper):
    SRC_NAME = "msigdb"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    BASE_URL = "https://data.broadinstitute.org/gsea-msigdb/msigdb/release/"
    VERSION_HOME = "https://software.broadinstitute.org/cancer/software/gsea/wiki/index.php/MSigDB_Latest_Release_Notes"
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
        release_notes = self.client.get(self.__class__.VERSION_HOME)
        html = bs4.BeautifulSoup(release_notes.text, "html.parser")
        content = html.find("div", {"id": "content"})
        p = content.find_all("p")
        version_txt = p[0].find("a").text
        version = version_txt.replace("MSigDB_v", "").replace(".Hs_Release_Notes", "")
        return version

    def create_todump_list(self, force=False):
        """Dump XML geneset file.
        NOTE: the "mouse" dataset was commented out because on inspection, it contains much of the same
        data as the "human" dataset. In fact, both datasets contain genesets from multiple species,
        only converted using homology. In the parser, we are taking the original ids, pre-homology conversion.
        If we keep both datasets, it causes a lot of _id clashes because of this redundancy.
        """
        self.release = self.get_remote_version()
        if force or not self.current_release or float(self.release) > float(self.current_release):
            home = self.__class__.BASE_URL
            long_version_str = "msigdb_v" + self.release  # Should have the format "msigdb_v2022.1"
            human_file_name = long_version_str + '.Hs_files_to_download_locally.zip'
            # mouse_file_name = long_version_str + '.Mm_files_to_download_locally.zip'
            # The url for human file should look like this:
            # https://data.broadinstitute.org/gsea-msigdb/msigdb/release/2022.1.Hs/msigdb_v2022.1.Hs_files_to_download_locally.zip
            human_url = home + self.release + '.Hs/' + human_file_name
            # The url for the mouse file should look like this:
            # https://data.broadinstitute.org/gsea-msigdb/msigdb/release/2022.1.Mm/msigdb_v2022.1.Mm_files_to_download_locally.zip
            # mouse_url = home + self.release + '.Mm/' + mouse_file_name
            self.human_data_file = os.path.join(self.new_data_folder, human_file_name)
            # self.mouse_data_file = os.path.join(self.new_data_folder, mouse_file_name)
            self.to_dump.append({"remote": human_url, "local": self.human_data_file})
            # self.to_dump.append({"remote": mouse_url, "local": self.mouse_data_file})

    def sort_xml(self, file, output_file):
        """Sort XML file by organism
        Args:
            file (str): path to XML file
            output_file (str): path to new XML file
        """
        original_xml = ET.parse(file)
        logging.info(f"Sorting documents in XML file: {file}")
        # Use XSLT file to sort XML file
        xslt = ET.parse(os.path.join(os.path.dirname(__file__), "sort_genesets.xsl"))
        transform = ET.XSLT(xslt)
        new_xml = transform(original_xml)
        with open(output_file, 'wb') as f:
            new_xml.write(f, pretty_print=True, encoding='utf-8')

    def post_dump(self, *args, **kwargs):
        """"Create a new XML file with genesets sorted by organism"""
        self.logger.info("Sorting documents in XML file")
        unzipall(self.new_data_folder)
        human_file_path = glob.glob(self.human_data_file.replace(".zip", "") + "/msigdb_v*.Hs.xml")
        # mouse_file_path = glob.glob(self.mouse_data_file.replace(".zip", "") + "/msigdb_v*.Mm.xml")
        self.sort_xml(human_file_path[0], os.path.join(self.new_data_folder, "human_genesets.xml"))
        # self.sort_xml(mouse_file_path[0], os.path.join(self.new_data_folder, "mouse_genesets.xml"))
