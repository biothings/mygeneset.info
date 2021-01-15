import re

from biothings.utils.web.es_dsl import AsyncSearch
from biothings.web.pipeline import ESQueryBuilder


class MyGenesetQueryBuilder(ESQueryBuilder):


    def _extra_query_options(self, search, options):

         if options.species:
             if not options.species:
                #if 'all' not in options.species:
                    search = search.filter('terms', taxid=options.species)
            if options.aggs and options.species_facet_filter:
                search = search.post_filter('terms', taxid=options.species_facet_filter)
