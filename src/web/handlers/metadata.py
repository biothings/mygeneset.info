"""
API handler for MyGeneset submit/ endpoint
"""


from biothings.web.handlers import MetadataSourceHandler
from elasticsearch.exceptions import NotFoundError

class MyGenesetMetadataSourceHandler(MetadataSourceHandler):
    """"
    Handler for GET /metadata

    {
        ...
        "stats": {
            "total": 10,
            "curated": 6,
            "user": 4,
            "anonymous": 2
        }
        ...
    }
    """

    async def _count_curated(self):
        """Fetch a geneset document from Elasticsearch"""
        try:
            result = await self.biothings.elasticsearch.async_client.count(
                    index=self.biothings.config.ES_CURATED_INDEX)
            return result['count']
        except NotFoundError:
            return 0

    async def _count_user(self):
        """Fetch a geneset document from Elasticsearch"""
        try:
            result = await self.biothings.elasticsearch.async_client.count(
                    index=self.biothings.config.ES_USER_INDEX)
            return result['count']
        except NotFoundError:
            return 0

    async def _count_anonymous(self):
        """Fetch a geneset document from Elasticsearch"""
        try:
            result = await self.biothings.elasticsearch.async_client.count(
                    '{"query": {"bool": {"must_not": {"exists": {"field": "author"}}}}}',
                    index=self.biothings.config.ES_USER_INDEX)
            return result['count']
        except NotFoundError:
            return 0

    async def get(self):
        info = await self.metadata.refresh(self.biothing_type)
        meta = self.metadata.get_metadata(self.biothing_type)

        if self.args.raw:
            raise Finish(info)

        elif self.args.dev:
            meta['software'] = self.biothings.devinfo.get()

        else:  # remove debug info
            for field in list(meta):
                if field.startswith('_'):
                    meta.pop(field, None)

        meta = await self.extras(meta)  # override here
        self.finish(dict(sorted(meta.items())))

    async def extras(self, _meta):
        _meta['stats']['curated'] = await self._count_curated()
        _meta['stats']['user'] = await self._count_user()
        _meta['stats']['anonymous'] = await self._count_anonymous()

        return _meta
