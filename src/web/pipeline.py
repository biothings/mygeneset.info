import re

from biothings.utils.web.es_dsl import AsyncSearch
from biothings.web.handlers.exceptions import BadRequest
from biothings.web.pipeline import ESQueryBuilder


class MyGenesetQueryBuilder(ESQueryBuilder):

    def default_string_query(self, q, options):
        search = super().default_string_query(q, options)
        search = self._extra_query_options(search, options)
        return search

    def default_match_query(self, q, options):
        search = super().default_match_query(q, options)
        search = self._extra_query_options(search, options)
        return search

    def build_string_query(self, q, options):
        search = super().build_string_query(q, options)
        search = self._extra_query_options(search, options)
        return search

    def build_match_query(self, q, options):
        search = super().build_match_query(q, options)
        search = self._extra_query_options(search, options)
        return search

    def _extra_query_options(self, search, options):
        search = AsyncSearch().query( "function_score", query=search.query,
                functions=[
                    {"filter": {"term": {"taxid": 9606}}, "weight": "1.55"},  # human
                    {"filter": {"term": {"taxid": 10090}}, "weight": "1.3"},  # mouse
                    {"filter": {"term": {"taxid": 10116}}, "weight": "1.1"},  # rat
                    ], score_mode="first")
        if options.species:
            search = search.filter('terms', taxid=options.species)
        return search
