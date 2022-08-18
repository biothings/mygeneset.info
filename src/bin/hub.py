#!/usr/bin/env python
import os
from functools import partial

import biothings
import config
from biothings.utils.version import set_versions

app_folder, _src = os.path.split(os.path.split(os.path.split(os.path.abspath(__file__))[0])[0])
set_versions(config, app_folder)
biothings.config_for_app(config)
logging = config.logger

import biothings.hub.databuild.builder as builder
from biothings.hub import HubServer

import hub.dataload.sources
from hub.databuild.mapper import MyGenesetMapper


class MyGenesetHubServer(HubServer):

    def configure_build_manager(self):
        mygeneset_mapper = MyGenesetMapper(name="count_genes")
        partial_builder = partial(builder.DataBuilder, mappers=[mygeneset_mapper])
        build_manager = builder.BuilderManager(job_manager=self.managers["job_manager"],
                                               builder_class=partial_builder)
        build_manager.configure()
        build_manager.poll()
        self.managers["build_manager"] = build_manager


server = MyGenesetHubServer(hub.dataload.sources, name=config.HUB_NAME)


if __name__ == "__main__":
    logging.info("Hub DB backend: %s", biothings.config.HUB_DB_BACKEND)
    logging.info("Hub database: %s", biothings.config.DATA_HUB_DB_DATABASE)
    server.start()
