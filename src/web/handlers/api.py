"""
API handler for MyGeneset submit/ endpoint
"""

import json
from datetime import datetime, timezone

import elasticsearch
from biothings.utils.dataload import dict_sweep
from biothings.web.auth.authn import BioThingsAuthnMixin
from biothings.web.handlers import BaseAPIHandler
from biothings.web.handlers.query import BiothingHandler, QueryHandler
from tornado.web import HTTPError
from utils.mygene_lookup import MyGeneLookup


class MyGenesetQueryHandler(BioThingsAuthnMixin, QueryHandler):
    """"Handler for /{ver}/query endpoint."""
    def prepare(self):
        super().prepare()
        if self.current_user:
            self.args['current_user'] = self.current_user['username']


class MyGenesetBiothingHandler(BioThingsAuthnMixin, BiothingHandler):
    """"Handler for /{ver}/geneset endpoint."""
    def prepare(self):
        super().prepare()
        if self.current_user:
            self.args['current_user'] = self.current_user['username']


class UserGenesetHandler(BioThingsAuthnMixin, BaseAPIHandler):
    """
        Operations on user geneset documents.
        Create - POST ./user_geneset/
        Update - PUT ./user_geneset/<_id>
        Remove - DELETE ./user_geneset/<_id>
    """

    def user_authenticated(func):
        """Checks if user is authenticated and sends 401 if not authenticated. """
        def _(self, *args, **kwargs):
            if not self.current_user:
                self.send_error(
                    message='You must log in first.',
                    status_code=401)
                return
            return func(self, *args, **kwargs)
        return _

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
        mygene = MyGeneLookup(species="all", cache_dict={})
        mygene.query_mygene(genes, id_types="_id")
        results = mygene.get_results(genes)
        return results

    async def _create_user_geneset(self, name, author, genes=[], is_public=True, description=""):
        """"Create a user geneset document."""
        geneset = await self._query_mygene(genes)
        geneset.update(
            {
                "name": name,
                "author": author,
                "description": description,
                "is_public": is_public
            }
        )
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
            if is_public in [False, "false", "False", "0"]:
                payload['is_public'] = False
            elif is_public in [True, "true", "True", "1"]:
                payload['is_public'] = True
            else:
                raise HTTPError(400, reason="Body element 'is_public' must be 'True/False', 'true/false', or '1/0'.")
        # genes
        if request_type == 'POST':
            if payload.get("genes") is None:
                raise HTTPError(400, reason="Body element 'genes' is required.")
        return payload

    @user_authenticated
    async def post(self):
        """Create a user geneset."""
        # Get user id
        user = self.current_user['username']
        # Get geneset parameters from request body
        if not self.request.body:
            raise HTTPError(400, reason="Expecting a JSON body.")
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
                "_id": response['_id'],
                "name": name,
                "author": user,
                "count": geneset['count']
            })
        else:
            # Return the document itself as the response
            self.finish({"new_document": geneset})

    @user_authenticated
    async def put(self, _id):
        """Update an existing user geneset"""
        user = self.current_user['username']
        payload = json.loads(self.request.body)
        payload = self._validate_input(self.request.method, payload)
        # Retrieve document
        document = await self._get_geneset(_id)
        # Check if user has permission to update document
        document_name = document['_source']['name']
        document_owner = document['_source']['author']
        geneset = document['_source']
        if document_owner == user:
            # Update metadata
            for elem in ['name', 'description', 'is_public']:
                if payload.get(elem) is not None:
                    geneset.update({elem: payload[elem]})
            # Update genes
            if payload.get('genes'):
                gene_operation = self.get_argument("gene_operation", None)
                if gene_operation is None:
                    raise HTTPError(400, reason="Missing argument 'gene_operation'.")
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
                    # Update count
                    geneset["count"] = len(geneset["genes"])
                elif gene_operation == "add":
                    query_results = await self._query_mygene(payload['genes'])
                    new_genes = query_results['genes']
                    geneset.update({
                        'genes': geneset['genes'] + [gene for gene in new_genes if gene not in geneset['genes']]})
                    # Update count
                    geneset["count"] = len(geneset["genes"])
                else:
                    raise HTTPError(
                        400,
                        reason="Argument 'gene operation' must be one of: 'replace', 'add', 'remove'."
                    )
            dry_run = self.get_argument("dry_run", default=None)
            if dry_run is None or dry_run.lower() == "false":
                _now = datetime.now(timezone.utc).isoformat()
                geneset.update({'updated': _now})
                response = await self.biothings.elasticsearch.async_client.update(
                        id=_id, body={"doc": geneset}, index=self.biothings.config.ES_USER_INDEX)
                self.finish({
                    "success": True,
                    "result": response['result'],
                    "_id": response['_id'],
                    "name": document_name,
                    "author": document_owner,
                    "count": geneset['count']
                })
            else:
                self.finish({"new_document": geneset})
        else:
            raise HTTPError(
                403,
                reason="You don't have permission to modify this document."
            )

    @user_authenticated
    async def delete(self, _id):
        """Delete a geneset."""
        user = self.current_user['username']
        # Retrieve document
        document = await self._get_geneset(_id)
        # Delete document if user has permission
        document_name = document['_source']['name']
        document_owner = document['_source'].get('author')
        if document_owner == user:
            response = await self.biothings.elasticsearch.async_client.delete(
                    id=_id, index=self.biothings.config.ES_USER_INDEX)
            self.finish({
                "success": True,
                "result": response['result'],
                "_id": response['_id'],
                "name": document_name,
                "author": document_owner
            })
        else:
            raise HTTPError(
                403,
                reason="You don't have permission to delete this document."
            )
