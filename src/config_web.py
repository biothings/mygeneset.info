import copy
import re
from biothings.web.settings.default import APP_LIST, ANNOTATION_KWARGS, QUERY_KWARGS

# *****************************************************************************
# Elasticsearch variables
# *****************************************************************************
# elasticsearch server transport url
ES_HOST = 'localhost:9200'
# elasticsearch index name
ES_INDEX = 'mygeneset_current'
# elasticsearch document type
ES_DOC_TYPE = 'geneset'

# *****************************************************************************
# Web Application
# *****************************************************************************
API_VERSION = 'v1'
# *****************************************************************************
# Analytics & Features
# *****************************************************************************

GA_ACTION_QUERY_GET = 'query_get'
GA_ACTION_QUERY_POST = 'query_post'
GA_ACTION_ANNOTATION_GET = 'geneset_get'
GA_ACTION_ANNOTATION_POST = 'geneset_post'
GA_TRACKER_URL = 'MyGeneset.info'

STATUS_CHECK = {
    'id': 'WP4966',
    'index': 'mygeneset_current',
    'doc_type': 'geneset'
}


# *****************************************************************************
# Query Customizations
# *****************************************************************************


#TAX_REDIRECT = "http://t.biothings.io/v1/taxon/{0}?include_children=1"

#APP_LIST += [
#        (r"/{ver}/species/(\d+)/?", "tornado.web.RedirectHandler", {"url": TAX_REDIRECT}),
#        (r"/{ver}/taxon/(\d+)/?", "tornado.web.RedirectHandler", {"url": TAX_REDIRECT})
#        ]


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
        'group': 'esqb',
        'translations': [
            (re.compile(pattern, re.I), translation['taxid'])
            for (pattern, translation) in TAXONOMY.items()
        ]
    },
    'species_facet_filter': {
        'type': list,
        'default': None,
        'max': 1000,
        'group': 'esqb',
        'translations': [
            (re.compile(pattern, re.I), translation['taxid']) for
            (pattern, translation) in TAXONOMY.items()
        ]
    }
}

ANNOTATION_DEFAULT_SCOPES = ['_id']
ANNOTATION_KWARGS = copy.deepcopy(ANNOTATION_KWARGS)
ANNOTATION_KWARGS['*'].update(SPECIES_TYPEDEF)

QUERY_KWARGS = copy.deepcopy(QUERY_KWARGS)
QUERY_KWARGS['*'].update(SPECIES_TYPEDEF)

SOURCES = [
    'ctd', 'do', 'go', 'kegg', 'msigdb', 'reactome', 'smpdb', 'wikipathways',
]

SOURCE_TYPEDEF = {
    'source': {
        'type': list,
        'default': ['all'],
        'max': 1000,
        'group': 'esqb',
        'translations': [
            (re.compile(src, re.I), src) for src in SOURCES
        ]
    },
    'source_facet_filter': {
        'type': list,
        'default': None,
        'max': 1000,
        'group': 'esqb',
        'translations': [
            (re.compile(src, re.I), src) for src in SOURCES
        ]
    }
}

ANNOTATION_KWARGS['*'].update(SOURCE_TYPEDEF)
QUERY_KWARGS['*'].update(SOURCE_TYPEDEF)

DEFAULT_FIELDS = ['_id', 'genes', 'name', 'description', 'source',
                  'author', 'date', 'taxid']
QUERY_KWARGS['*']['_source']['default'] = DEFAULT_FIELDS

QUERY_KWARGS['POST']['scopes']['default'] =  ['_id', 'name']

ES_QUERY_BUILDER = "web.pipeline.MyGenesetQueryBuilder"
