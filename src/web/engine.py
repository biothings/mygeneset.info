import config
from biothings.web.query import AsyncESQueryBackend


class MyGenesetQueryBackend(AsyncESQueryBackend):
    def adjust_index(self, original_index, query, **options):

        index = original_index  # keep original if include is public
        include = options.get("include")

        if include:
            if include == "curated":
                index = config.ES_CURATED_INDEX
            elif include in ["user", "anonymous"]:
                index = config.ES_USER_INDEX

        return index
