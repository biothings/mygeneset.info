#!/usr/bin/env python
import logging
import os

import biothings
import config
from biothings.utils.version import set_versions

app_folder, _src = os.path.split(os.path.split(os.path.split(os.path.abspath(__file__))[0])[0])
set_versions(config, app_folder)
biothings.config_for_app(config)

from biothings.hub import HubServer

class MyGenesetHubServer(HubServer):

    def configure_build_manager(self):
        import biothings.hub.databuild.builder as builder
        from hub.databuild.builder import MyGenesetDataBuilder
        # set specific managers
        build_manager = builder.BuilderManager(builder_class=MyGenesetDataBuilder,job_manager=self.managers["job_manager"])
        build_manager.configure()
        self.managers["build_manager"] = build_manager
        self.logger.info("Using custom builder %s" % MyGenesetDataBuilder)

import hub.dataload.sources

server = MyGenesetHubServer(hub.dataload.sources, name=config.HUB_NAME)

if __name__ == "__main__":
    logging.info("Hub DB backend: %s", biothings.config.HUB_DB_BACKEND)
    logging.info("Hub database: %s", biothings.config.DATA_HUB_DB_DATABASE)
    server.start()
