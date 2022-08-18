# ######### #
# HUB VARS  #
# ######### #


# Hub name/icon url/version, for display purpose
HUB_NAME = "MyGeneset.info API (backend)"
HUB_ICON = "https://raw.githubusercontent.com/biothings/mygeneset.info/master/mygeneset.png"

# Pre-prod/test ES definitions
INDEX_CONFIG = {
    #"build_config_key" : None, # used to select proper idxr/syncer
    "indexer_select": {
        # default
        #None : "path.to.special.Indexer",
    },
    "env" : {
        "local": {
            "host": "localhost:9200",
            "indexer": {
                "args": {
                    "timeout": 300,
                    "retry_on_timeout": True,
                    "max_retries": 10,
                    },
                },
            "index": [
                        {
                    "doc_type": "geneset",
                    "index": "mygeneset_current"
                    }
                ],
        }
    },
}

# Snapshot environment configuration
SNAPSHOT_CONFIG = {}
RELEASE_CONFIG = {}


########################################
# APP-SPECIFIC CONFIGURATION VARIABLES #
########################################
# The following variables should or must be defined in your
# own application. Create a config.py file, import that config_common
# file as:
#
#   from config_hub import *
#
# then define the following variables to fit your needs. You can also override any
# any other variables in this file as required. Variables defined as ValueError() exceptions
# *must* be defined
#

