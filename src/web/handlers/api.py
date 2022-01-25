"""
API handler for MyGeneset submit/ endpoint
"""

import json
from datetime import datetime, timezone

import elasticsearch
from biothings.utils.dataload import dict_sweep
from biothings.web.auth.authn import BioThingsAuthnMixin
from biothings.web.handlers import BaseAPIHandler
from biothings.web.handlers.query import QueryHandler, BiothingHandler
from tornado.web import HTTPError
from utils.geneset_utils import IDLookup


class MyGenesetQueryHandler(BioThingsAuthnMixin, QueryHandler):
    def prepare(self):
        super().prepare()
        if self.current_user:
            self.args['current_user'] = self.current_user['login']


class MyGenesetBiothingHandler(BioThingsAuthnMixin, BiothingHandler):
    def prepare(self):
        super().prepare()
        if self.current_user:
            self.args['current_user'] = self.current_user['login']


class UserInfoHandler(BioThingsAuthnMixin, BaseAPIHandler):
    def get(self):
        if self.current_user:
            self.write(self.current_user)
        else:
            header = self.get_www_authenticate_header()
            if header:
                self.clear()
                self.set_header('WWW-Authenticate', header)
                self.set_status(401, "Unauthorized")
                # raising HTTPError will cause headers to be emptied
                self.finish()
            else:
                raise HTTPError(403)


class UserGenesetHandler():
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
        mygene = IDLookup(species="all", cache_dict={})
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
                gene_operation = self.get_argument("gene_operation", None)
                if gene_operation is None:
                    raise HTTPError(401, reason="Missing argument 'gene_operation'.")
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
