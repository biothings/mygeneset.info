import re

from biothings.utils.web.es_dsl import AsyncSearch
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

    def _extra_query_options(self, search, options):
        if options.species:
            search = search.filter('terms', taxid=options.species)
        return search
