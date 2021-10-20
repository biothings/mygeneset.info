import copy
import re

from biothings.web.settings.default import ANNOTATION_KWARGS, QUERY_KWARGS, APP_LIST

# *****************************************************************************
# Elasticsearch variables
# *****************************************************************************
ES_HOST = 'localhost:9200'
# elasticsearch index name
ES_INDEX = 'mygeneset_current,user_genesets'
ES_USER_INDEX = 'user_genesets'
# elasticsearch document type
ES_DOC_TYPE = 'geneset'


# *****************************************************************************
# Web Application
# *****************************************************************************
APP_VERSION = 'v1'

# *****************************************************************************
# Features
# *****************************************************************************

STATUS_CHECK = {
    'id': 'WP4966',
    'index': 'mygeneset_current'
}


# *****************************************************************************
# Query Customizations
# *****************************************************************************


APP_LIST += [
        (r"/{ver}/query/?", "web.handlers.api.QueryHandler"),
        (r"/{ver}/geneset/?", "web.handlers.api.BiothingHandler"),
        (r"/{ver}/user_geneset/?", "web.handlers.api.UserGenesetHandler"),
        (r"/{ver}/user_geneset/([^/]+)/?", "web.handlers.api.UserGenesetHandler"),
        (r"/login", "home.mockLogin"),
        (r"/login/github", "web.handlers.auth.GitHubAuthHandler"),
        (r"/login/orcid", "web.handlers.auth.ORCIDAuthHandler"),
        (r"/logout", "web.handlers.auth.LogoutHandler"),
        (r"/user", "web.handlers.auth.UserInfoHandler"),
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
    "brewers-yeast": {"taxid": "559292"}
}

SPECIES_TYPEDEF = {
    'species': {
        'type': list,
        'default': ['all'],
        'max': 1000,
        'translations': [
            (re.compile(pattern, re.I), translation['taxid'])
            for (pattern, translation) in TAXONOMY.items()
        ]
    },
    'species_facet_filter': {
        'type': list,
        'default': None,
        'max': 1000,
        'translations': [
            (re.compile(pattern, re.I), translation['taxid']) for
            (pattern, translation) in TAXONOMY.items()
        ]
    }
}

SOURCE_TYPEDEF = {
    'source': {
        'type': list,
        'default': ['all'],
        'max': 1000,
    },
    'source_facet_filter': {
        'type': list,
        'default': None,
        'max': 1000,
    }
}

ANNOTATION_DEFAULT_SCOPES = ['_id']
ANNOTATION_KWARGS = copy.deepcopy(ANNOTATION_KWARGS)
ANNOTATION_KWARGS['*'].update(SPECIES_TYPEDEF)
ANNOTATION_KWARGS['*'].update(SOURCE_TYPEDEF)

QUERY_KWARGS = copy.deepcopy(QUERY_KWARGS)
QUERY_KWARGS['*'].update(SPECIES_TYPEDEF)
QUERY_KWARGS['*'].update(SOURCE_TYPEDEF)
QUERY_KWARGS['*']['_source']['default'] = [
    '_id', 'genes', 'name', 'description',
    'source', 'author', 'date', 'taxid']
QUERY_KWARGS['POST']['scopes']['default'] = [
    '_id', 'name']

ES_QUERY_BUILDER = "web.pipeline.MyGenesetQueryBuilder"


# A random string -- set in config.py
COOKIE_SECRET = ""

# OAuth keys -- set in config.py
GITHUB_CLIENT_ID = ""
GITHUB_CLIENT_SECRET = ""
ORCID_CLIENT_ID = ""
ORCID_CLIENT_SECRET = ""
