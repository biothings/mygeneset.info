import os

import biothings
import bs4
import config

biothings.config_for_app(config)

from biothings.hub.dataload.dumper import HTTPDumper
from config import DATA_ARCHIVE_ROOT


class WikiPathwaysDumper(HTTPDumper):

    SRC_NAME = "wikipathways"
    SRC_ROOT_FOLDER = os.path.join(DATA_ARCHIVE_ROOT, SRC_NAME)
    BASE_URL = "http://data.wikipathways.org/current/gmt/"
    SCHEDULE = "0 5 15 * *"

    def get_remote_version(self):
        home = self.client.get(self.__class__.BASE_URL)
        html = bs4.BeautifulSoup(home.text, "html.parser")
        # Grab the date string from the text of the first link element
        table = html.find("table")
        link = table.find("a")
        if link is None:
            self.logger.error("No links found in source.")
        else:
            release_str = link.contents[0].split("-")
            assert release_str[0] == "wikipathways", (
                "Source link should start with 'wikipathways': %s" % release_str
            )
            version = release_str[1]
            assert len(version) == 8, "Version number should be 8 characters long: %s" % version
            return version

    def create_todump_list(self, force=False):
        self.release = self.get_remote_version()
        if force or not self.current_release or int(self.release) > int(self.current_release):
            home = self.client.get(self.__class__.BASE_URL)
            html = bs4.BeautifulSoup(home.text, "html.parser")
            for tr_tag in html.find_all("tr"):
                a_tag = tr_tag.find("a")
                if a_tag is not None:
                    name = a_tag.contents[0]
                    url = self.__class__.BASE_URL + name
                    local_file = os.path.join(self.new_data_folder, name)
                    self.to_dump.append({"remote": url, "local": local_file})
