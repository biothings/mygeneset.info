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

import hub.dataload.sources

server = HubServer(hub.dataload.sources, name=config.HUB_NAME)


if __name__ == "__main__":
    logging.info("Hub DB backend: %s", biothings.config.HUB_DB_BACKEND)
    logging.info("Hub database: %s", biothings.config.DATA_HUB_DB_DATABASE)
    server.start()
