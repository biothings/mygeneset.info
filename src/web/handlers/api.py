"""
API handler for MyGeneset submit/ endpoint
"""

import json
import logging

from biothings.web.handlers.exceptions import BadRequest, EndRequest
from biothings.web.handlers import BaseAPIHandler
from biothings.web.handlers import BiothingHandler

from jose import jwt
from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler, Finish, HTTPError


class BaseHandler(BaseAPIHandler):

    def get_current_user(self):
           user_json = self.get_secure_cookie("user")
           if not user_json:
               return None
           return json.loads(user_json.decode('utf-8'))


class UserGenesetsHandler(BaseHandler):

    index = "user-genesets-test"

    async def post(self):
        """Create a new geneset"""
        header = {"Content-Type": "application/json"}
        payload = self.request.body
        url = "http://{}/{}/_doc/?pretty".format(self.host, self.index)
        client = AsyncHTTPClient()
        response = await client.fetch(
                url, method="POST", headers=header, body=payload)

    async def put(self):
        """Create a geneset with a specific id or update an existing geneset"""
        payload = self.request.body
        header = {"Content-Type": "application/json"}

        geneset_id = self.get_argument('geneset_id')
        url = "http://{}/{}/geneset/{}/_update?pretty".format(
                self.host, self.index, geneset_id)

        client = AsyncHTTPClient()
        response = await client.fetch(
                url, method="PUT", headers=header, body=payload)

    async def delete(self):
        """Delete a specific geneset."""

        client = AsyncHTTPClient()
        geneset_id = self.get_argument('geneset_id')
        url = "http://{}/{}/_doc/{}?pretty".format(
                self.host, self.index, geneset_id)
        response = await client.fetch(
                url, method="DELETE")
        logging.log(0, response)

