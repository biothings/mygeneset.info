
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
    'id': 'example_id',
    'index': 'mygeneset_current',
    'doc_type': 'geneset'
}

ANNOTATION_DEFAULT_SCOPES = [
    '_id']

