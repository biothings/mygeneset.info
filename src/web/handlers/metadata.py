"""
API handler for MyGeneset submit/ endpoint
"""


import elasticsearch
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

        _meta['stats']['curated'] = 180809
        _meta['stats']['user'] = 16
        _meta['stats']['anonymous'] = 2

        return _meta
