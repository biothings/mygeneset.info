
import copy
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

# Customizations

ANNOTATION_DEFAULT_SCOPES = [
    '_id']

TAX_REDIRECT = "http://t.biothings.io/v1/taxon/{0}?include_children=1"

APP_LIST += [
        (r"/{ver}/species/(\d+)/?", "tornado.web.RedirectHandler", {"url": TAX_REDIRECT}),
        (r"/{ver}/taxon/(\d+)/?", "tornado.web.RedirectHandler", {"url": TAX_REDIRECT})
        ]


TAXONOMY = {
    "human": {"tax_id": "9606"},
    "mouse": {"tax_id": "10090"},
    "rat": {"tax_id": "10116"},
    "fruitfly": {"tax_id": "7227"},
    "nematode": {"tax_id": "6239"},
    "zebrafish": {"tax_id": "7955"},
    "thale-cress": {"tax_id": "3702"},
    "frog": {"tax_id": "8364"},
    "pig": {"tax_id": "9823"}
}

SPECIES_TYPEDEF = {
    'species': {
        'type': list,
        'default': ['all'],
        'max': 1000,
        'group': 'esqb',
        'translations': [
            (re.compile(pattern, re.I), translation['tax_id'])
            for (pattern, translation) in TAXONOMY.items()
        ]
    },
    'species_facet_filter': {
        'type': list,
        'default': None,
        'max': 1000,
        'group': 'esqb',
        'translations': [
            (re.compile(pattern, re.I), translation['tax_id']) for
            (pattern, translation) in TAXONOMY.items()
        ]
    }
}


DEFAULT_FIELDS = ['name', 'symbol', 'taxid']
ANNOTATION_DEFAULT_SCOPES = ["_id"]


ANNOTATION_KWARGS = copy.deepcopy(ANNOTATION_KWARGS)
ANNOTATION_KWARGS['*'].update(SPECIES_TYPEDEF)

QUERY_KWARGS['GET']['scopes']['default'] =  ["_id"]
QUERY_KWARGS['POST']['scopes']['default'] =  ["_id"]
QUERY_KWARGS['*']['_source']['default'] = DEFAULT_FIELDS

ES_QUERY_BUILDER = "web.pipeline.MyGenesetQueryBuilder"
