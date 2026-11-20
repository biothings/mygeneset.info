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
from biothings.hub.api import EndpointDefinition
from biothings.utils.hub import CommandDefinition
from utils.runtime import require_free_threading, runtime_info

import hub.dataload.sources

class MyGenesetHubServer(HubServer):
    def configure_commands(self):
        super().configure_commands()
        self.commands["runtime_info"] = CommandDefinition(command=runtime_info, tracked=False)

    def configure_api_endpoints(self):
        super().configure_api_endpoints()
        self.api_endpoints["runtime"] = EndpointDefinition(name="runtime_info", method="get")

    def before_start(self):
        super().before_start()
        logging.info("Hub runtime: %s", require_free_threading())


server = MyGenesetHubServer(hub.dataload.sources, name=config.HUB_NAME)


if __name__ == "__main__":
    logging.info("Hub DB backend: %s", biothings.config.HUB_DB_BACKEND)
    logging.info("Hub database: %s", biothings.config.DATA_HUB_DB_DATABASE)
    server.start()
