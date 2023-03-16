from biothings.web.query import AsyncESQueryBackend

import config

class MyGenesetQueryBackend(AsyncESQueryBackend):

    def adjust_index(self, original_index, query, **options):

        index = original_index # keep original if include is public
        include = options.get("include")

        if options.get("include"):
            if options.get("include") == "curated":
                index = config.ES_CURATED_INDEX
            elif options.get("include") in ["user", "anonymous"]:
                index = config.ES_USER_INDEX

        return index
