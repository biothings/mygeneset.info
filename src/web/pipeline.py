from biothings.web.query import ESQueryBuilder
from elasticsearch_dsl import Q, Search
from tornado.web import HTTPError

import config

class MyGenesetQueryBuilder(ESQueryBuilder):

    def apply_extras(self, search, options):

        search = Search().query(
            "function_score", query=search.query, score_mode="first", functions=[
                {"filter": {"term": {"taxid": 9606}}, "weight": "1.55"},  # human
                {"filter": {"term": {"taxid": 10090}}, "weight": "1.3"},  # mouse
                {"filter": {"term": {"taxid": 10116}}, "weight": "1.1"},  # rat
            ])

        # Filter results according to authenticated user permissions
        if options.current_user is not None:
            search = search.filter(Q("match", is_public=True) | Q("match", author=options.current_user))
        else:
            search = search.filter(Q('match', is_public=True))

        if options.species:
            if 'all' in options.species:
                pass
            elif not all(isinstance(string, str) for string in options.species):
                raise HTTPError(400, reason="species must be strings or integer strings.")
            elif not all(string.isnumeric() for string in options.species):
                raise HTTPError(400, reason="cannot map some species to taxids.")
            else:
                search = search.filter('terms', taxid=options.species)
            if options.aggs and options.species_facet_filter:
                search = search.post_filter('terms', taxid=options.species_facet_filter)

        if options.source:
            if 'all' in options.source:
                pass
            elif not all(isinstance(src, str) for src in options.source):
                raise HTTPError(400, reason="source must be strings.")
            else:
                search = search.filter('terms', source=options.source)

            if options.aggs and options.source_facet_filter:
                search = search.post_filter('terms', source=options.source_facet_filter)

        if options.include:
            if options.include == 'public':
                search = search.filter('match', is_public=True)
            elif options.include == 'curated':
                search = search.filter('match', _index=config.ES_CURATED_INDEX)
            elif options.include == 'user':
                search = search.filter('match', _index=config.ES_USER_INDEX)
            elif options.include == 'anonymous':
                search = search.filter('match', _index=config.ES_USER_INDEX).exclude('exists', field="author")

        return super().apply_extras(search, options)
