"""
API handler for MyGeneset submit/ endpoint
"""


import elasticsearch
from elasticsearch import Elasticsearch
from biothings.web.handlers import MetadataSourceHandler
from tornado.web import HTTPError

class MyGenesetMetadataSourceHandler(MetadataSourceHandler):
    """"
    Handler for GET /metadata

    {
        ...
        "stats": {
        "total": 180825,
        "curated": 180809,
        "user": 16,
        "anonymous": 2
        }
        ...
    }
    """

    async def _count_curated(self):
        """Fetch a geneset document from Elasticsearch"""
        try:
            document = await self.biothings.elasticsearch.async_client.get(
                    index=self.biothings.config.ES_INDEX)
        except elasticsearch.exceptions.NotFoundError:
            raise HTTPError(404, None, "_count_curated", reason="Document does not exist.")
        return document

    async def _count_user(self):
        """Fetch a geneset document from Elasticsearch"""
        try:
            document = await self.biothings.elasticsearch.async_client.get(
                    index=self.biothings.config.ES_USER_INDEX)
        except elasticsearch.exceptions.NotFoundError:
            raise HTTPError(404, None, "_count_user", reason="Document does not exist.")
        return document

    async def _count_anonymous(self):
        """Fetch a geneset document from Elasticsearch"""
        try:
            document = await self.biothings.elasticsearch.async_client.get(
                    index=self.biothings.config.ES_USER_INDEX)
        except elasticsearch.exceptions.NotFoundError:
            raise HTTPError(404, None, "_count_anonymous", reason="Document does not exist.")
        return document

    def extras(self, _meta):

        ES_HOST = 'es8.biothings.io'
        ES_PORT = '9200'
        ES_INDEX = 'mygeneset_current'
        ES_USER_INDEX = 'mygeneset_current_user_genesets'
        ES_DOC_TYPE = 'geneset'

        # http://es8.biothings.io:9200/_cat/count/geneset_20230215_txbg0fnz_202302151151?format=JSON

        es = Elasticsearch('http://es8.biothings.io:9200')
        curated = es.count(index=ES_INDEX, body={ "query": {"match_all" : { }}})['count']
        #user = es.count(index=ES_USER_INDEX, body={ "query": {"match_all" : { }}})['count']
        user = es.count(index=ES_USER_INDEX, body={"query" : {"term" : { "is_public" : "false" }}})['count']
        anonymous = es.count(index=ES_USER_INDEX, body={ "query": {"match_all" : { }}})['count']

        _meta['stats']['curated'] = curated
        _meta['stats']['user'] = user
        _meta['stats']['anonymous'] = anonymous

        return _meta
