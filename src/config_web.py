import copy
import re

from biothings.web.settings.default import ANNOTATION_KWARGS, APP_LIST, QUERY_KWARGS
from web.authn.authn_provider import UserCookieAuthProvider

# *****************************************************************************
# Elasticsearch variables
# *****************************************************************************
ES_HOST = "localhost:9200"
# elasticsearch index name
ES_CURATED_INDEX = "mygeneset_current"
ES_USER_INDEX = "mygeneset_current_user_genesets"
ES_INDEX = [ES_CURATED_INDEX, ES_USER_INDEX]
# elasticsearch document type
ES_DOC_TYPE = "geneset"


# *****************************************************************************
# Web Application
# *****************************************************************************
APP_VERSION = "v1"

# *****************************************************************************
# Features
# *****************************************************************************

STATUS_CHECK = {"id": "WP4966", "index": "mygeneset_current"}


# *****************************************************************************
# Query Customizations
# *****************************************************************************

# Update the default metadata handlers to use MyGenesetMetadataSourceHandler
for idx, handler in enumerate(APP_LIST):
    if handler[0].endswith("metadata/?"):
        APP_LIST[idx] = (handler[0], "web.handlers.metadata.MyGenesetMetadataSourceHandler")

APP_LIST += [
    (r"/{ver}/query/?", "web.handlers.api.MyGenesetQueryHandler"),
    (r"/{pre}/{ver}/{typ}(?:/([^/]+))?/?", "web.handlers.api.MyGenesetBiothingHandler"),
    (r"/{ver}/user_geneset/?", "web.handlers.api.UserGenesetHandler"),
    (r"/{ver}/user_geneset/([^/]+)/?", "web.handlers.api.UserGenesetHandler"),
    (r"/user_info", "web.handlers.login.UserInfoHandler"),
    (r"/xsrf_token", "xsrf.XSRFToken"),
    (r"/logout", "web.handlers.login.LogoutHandler"),
    (r"/login/github", "web.handlers.auth.GitHubLoginHandler"),
    (r"/login/orcid", "web.handlers.auth.ORCIDLoginHandler"),
]

TAXONOMY = {
    "human": {"taxid": "9606"},
    "mouse": {"taxid": "10090"},
    "rat": {"taxid": "10116"},
    "fruitfly": {"taxid": "7227"},
    "mosquito": {"taxid": "180454"},
    "nematode": {"taxid": "6239"},
    "zebrafish": {"taxid": "7955"},
    "thale-cress": {"taxid": "3702"},
    "rice": {"taxid": "39947"},
    "dog": {"taxid": "9615"},
    "chicken": {"taxid": "9031"},
    "horse": {"taxid": "9796"},
    "chimpanzee": {"taxid": "9598"},
    "frog": {"taxid": "8364"},
    "pig": {"taxid": "9823"},
    "pseudomonas-aeruginosa": {"taxid": "208964"},
    "brewers-yeast": {"taxid": "559292"},
}

SPECIES_TYPEDEF = {
    "species": {
        "type": list,
        "default": ["all"],
        "max": 1000,
        "translations": [
            (re.compile(pattern, re.I), translation["taxid"])
            for (pattern, translation) in TAXONOMY.items()
        ],
    },
    "species_facet_filter": {
        "type": list,
        "default": None,
        "max": 1000,
        "translations": [
            (re.compile(pattern, re.I), translation["taxid"])
            for (pattern, translation) in TAXONOMY.items()
        ],
    },
}

SOURCE_TYPEDEF = {
    "source": {
        "type": list,
        "default": ["all"],
        "max": 1000,
    },
    "source_facet_filter": {
        "type": list,
        "default": None,
        "max": 1000,
    },
}

INCLUDE_TYPEDEF = {
    "include": {
        "type": str,
        "default": "all",
        "enum": ("all", "curated", "public", "user", "anonymous"),
    }
}

ANNOTATION_DEFAULT_SCOPES = ["_id"]
ANNOTATION_KWARGS = copy.deepcopy(ANNOTATION_KWARGS)
ANNOTATION_KWARGS["*"].update(SPECIES_TYPEDEF)
ANNOTATION_KWARGS["*"].update(SOURCE_TYPEDEF)
ANNOTATION_KWARGS["*"].update(INCLUDE_TYPEDEF)

QUERY_KWARGS = copy.deepcopy(QUERY_KWARGS)
QUERY_KWARGS["*"].update(SPECIES_TYPEDEF)
QUERY_KWARGS["*"].update(SOURCE_TYPEDEF)
QUERY_KWARGS["*"].update(INCLUDE_TYPEDEF)
QUERY_KWARGS["*"]["_source"]["default"] = [
    "_id",
    "genes",
    "name",
    "description",
    "source",
    "author",
    "date",
    "taxid",
]
QUERY_KWARGS["POST"]["scopes"]["default"] = ["_id", "name"]

ES_QUERY_BUILDER = "web.pipeline.MyGenesetQueryBuilder"
ES_QUERY_BACKEND = "web.engine.MyGenesetQueryBackend"

# Authentication providers for BiothingsAuthnMixin
AUTHN_PROVIDERS = [(UserCookieAuthProvider, {})]

# A random string -- set in config.py
COOKIE_SECRET = ""

# OAuth keys -- set in config.py
GITHUB_CLIENT_ID = ""
GITHUB_CLIENT_SECRET = ""
ORCID_CLIENT_ID = ""
ORCID_CLIENT_SECRET = ""

# User geneset settings
MAX_GENESET_SIZE = 2000

# Web Server Hostname
# http://localhost:8000 for dev or https://mygeneset.info for prod

WEB_HOST = "https://mygeneset.info"
FRONTEND_PATH = ""
