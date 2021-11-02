"""
API handler for MyGeneset submit/ endpoint
"""

from datetime import datetime, timezone
import json
import re
from time import time

import elasticsearch
from biothings.utils.dataload import dict_sweep
from biothings.web.handlers.query import (BaseQueryHandler, capture_exceptions,
                                          ensure_awaitable)
import elasticsearch_dsl
from tornado.web import HTTPError
from utils.geneset_utils import IDLookup
from web.handlers.auth import BaseAuthHandler, authenticated_user


class QueryHandler(BaseQueryHandler, BaseAuthHandler):
    ''' Biothings Query Endpoint with User Authentication
    Fetch  - GET  ./query?q=<query_string>
    Fetch  - POST ./query?q=<query_string1, query_string2>
    '''
    name = 'query'

    def set_current_user(self, *args, **kwargs):
        """Add a query argument if user is authenticated"""
        current_user = self.get_current_user()
        if current_user is not None:
            self.args['current_user'] = current_user['login']


    async def post(self, *args, **kwargs):
        self.event['value'] = len(self.args['q'])

        self.set_current_user()

        result = await ensure_awaitable(
            self.pipeline.search(**self.args))
        self.finish(result)

    async def get(self, *args, **kwargs):
        self.event['value'] = 1

        self.set_current_user()

        if self.args.get('fetch_all'):
            self.event['label'] = 'fetch_all'

        if self.args.get('fetch_all') or \
                self.args.get('scroll_id') or \
                self.args.get('q') == '__any__':
            self.clear_header('Cache-Control')

        response = await ensure_awaitable(
            self.pipeline.search(**self.args))
        self.finish(response)


class BiothingHandler(BaseQueryHandler, BaseAuthHandler):
    """
    Biothings Annotation Endpoint with Authentication
    Fetch  - GET  ./geneset?q=<_id>
    Fetch  - POST ./geneset?ids=<_id,_id>
    """
    name = 'annotation'

    def set_current_user(self, *args, **kwargs):
        """Add a query argument if user is authenticated"""
        current_user = self.get_current_user()
        if current_user is not None:
            self.args['current_user'] = current_user['login']

    @capture_exceptions
    async def post(self, *args, **kwargs):
        self.event['value'] = len(self.args['id'])

        self.set_current_user()

        result = await ensure_awaitable(
            self.pipeline.fetch(**self.args))
        self.finish(result)

    @capture_exceptions
    async def get(self, *args, **kwargs):
        self.event['value'] = 1

        self.set_current_user()

        result = await ensure_awaitable(
            self.pipeline.fetch(**self.args))
        self.finish(result)


class UserGenesetHandler(BaseAuthHandler):
    """
        Operations on user geneset documents.
        Create - POST ./user_geneset/
        Update - PUT ./user_geneset/<_id>
        Remove - DELETE ./user_geneset/<_id>
    """
    def _get_user_id(self):
        user = self.get_current_user()
        return user['login']

    async def _get_geneset(self, _id):
        """Fetch a geneset document from Elasticsearch"""
        try:
            document = await self.biothings.elasticsearch.async_client.get(
                    id=_id,
                    index=self.biothings.config.ES_USER_INDEX)
        except elasticsearch.exceptions.NotFoundError:
            raise HTTPError(404, None, {"id": _id}, reason="Document does not exist.")
        return document

    async def _query_mygene(self, genes):
        """"Take a list of mygene.info ids and return a list of gene objects."""
        mygene = IDLookup(species="all")
        mygene.query_mygene(genes, id_type="_id")
        return [gene for gene in mygene.query_cache.values()]

    async def _create_user_geneset(self, name, author, genes=[], is_public=True, description=""):
        """"Create a user geneset document."""
        genes = await self._query_mygene(genes)
        geneset = {"name": name, "author": author, "description": description,
                   "is_public": is_public, "genes": genes}
        geneset = dict_sweep(geneset, vals=[None])
        return geneset

    def _validate_input(self, request_type, payload):
        """Validate request body."""
        genes = payload.get('genes')
        # name
        if request_type == "POST":
            if not payload.get("name"):
                raise HTTPError(400, reason="Missing required body element 'name'.")
        elif request_type == "PUT":
            if payload.get("name") == "":
                raise HTTPError(400, reason="Body element 'name' cannot be empty.")
        # is_public
        is_public = payload.get("is_public", "true")
        if is_public is not None:
            if is_public in [True, "false", "False", "0"]:
                payload['is_public'] = False
            elif is_public in [False, "true", "True", "1"]:
                payload['is_public'] = True
            else:
                raise HTTPError(400, reason="Body element 'is_public' must be 'True/False', 'true/false', or '1/0'.")
        # genes
        if request_type == 'POST':
            if payload.get("genes") is None:
                raise HTTPError(400, reason="Body element 'genes' is required.")
        return payload

    @authenticated_user
    async def post(self):
        """Create a user geneset."""
        # Get user id
        user = self._get_user_id()
        # Get geneset parameters from request body
        payload = json.loads(self.request.body)
        payload = self._validate_input(self.request.method, payload)
        name = payload['name']
        description = payload.get('description')
        genes = payload['genes']
        is_public = payload['is_public']
        # Generate body for ES request
        geneset = await self._create_user_geneset(name, user, genes, is_public, description)
        dry_run = self.get_argument("dry_run", default=None)
        if dry_run is None or dry_run.lower() == "false":
            _now = str(datetime.now(timezone.utc).replace(microsecond=0).isoformat())
            geneset.update({"created": _now})
            geneset.update({"updated": _now})
            response = await self.biothings.elasticsearch.async_client.index(
                body=geneset, index=self.biothings.config.ES_USER_INDEX)
            self.finish({
                "success": True,
                "result": response['result'],
                "_id":response['_id'],
                "name": name,
                "user": user
            })
        else:
            # Return the document itself as the response
            self.finish({"new_document": geneset})

    @authenticated_user
    async def put(self, _id):
        """Update an existing user geneset"""
        user = self._get_user_id()
        payload = json.loads(self.request.body)
        payload = self._validate_input(self.request.method, payload)
        # Retrieve document
        document = await self._get_geneset(_id)
        # Update document if user has permission
        document_name = document['_source']['name']
        document_owner =  document['_source']['author']
        geneset = document['_source']
        if document_owner == user:
            # Update metadata
            for elem in ['name', 'description', 'is_public']:
                if payload.get(elem):
                    geneset.update({elem: payload[elem]})
            # Update genes
            if payload.get('genes'):
                gene_operation = self.get_argument("gene_operation")
                if gene_operation == "replace":
                    geneset = await self._create_user_geneset(
                            name=geneset['name'],
                            genes=payload['genes'],
                            author=user,
                            description=geneset.get('description'),
                            is_public=geneset['is_public'])
                elif gene_operation == "remove":
                    gene_dict = {gene['mygene_id']: gene for gene in geneset['genes']}
                    for geneid in payload['genes']:
                        gene_dict.pop(geneid, None)
                    geneset.update({'genes': list(gene_dict.values())})
                elif gene_operation == "add":
                    new_genes = await self._query_mygene(payload['genes'])
                    geneset.update({
                        'genes': geneset['genes'] + [gene for gene in new_genes if gene not in geneset['genes']]})
                else:
                    raise HTTPError(401,
                        reason="Argument 'gene operation' must be one of: 'replace', 'add', 'remove'.")

            # Update geneset
            dry_run = self.get_argument("dry_run", default=None)
            if dry_run is None or dry_run.lower() == "false":
                _now = datetime.now(timezone.utc).isoformat()
                geneset.update({'updated': _now})
                response = await self.biothings.elasticsearch.async_client.update(
                        id=_id, body={"doc": geneset}, index=self.biothings.config.ES_USER_INDEX)
                self.finish({
                    "success": True,
                    "result": response['result'],
                    "_id":response['_id'],
                    "name": document_name,
                    "user": document_owner
                })
            else:
                self.finish({"new_document": geneset})
        else:
            raise HTTPError(403,
                reason="You don't have permission to modify this document.")

    @authenticated_user
    async def delete(self, _id):
        """Delete a geneset."""
        user = self._get_user_id()
        # Retrieve document
        document = await self._get_geneset(_id)
        # Delete document if user has permission
        document_name = document['_source']['name']
        document_owner =  document['_source'].get('author')
        if document_owner == user:
            response = await self.biothings.elasticsearch.async_client.delete(
                    id=_id, index=self.biothings.config.ES_USER_INDEX)
            self.finish({
                "success": True,
                "result": response['result'],
                "_id": response['_id'],
                "name": document_name,
                "user": document_owner
            })
        else:
            raise HTTPError(403,
                reason="You don't have permission to delete this document.")