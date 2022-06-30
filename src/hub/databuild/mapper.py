import biothings, config
biothings.config_for_app(config)

import biothings.hub.databuild.mapper as mapper



class MyGenesetMapper(mapper.BaseMapper):
    """"Count the number of genes in each geneset"""

    def load(self):
        pass

    def process(self, docs):
        for doc in docs:
            doc['count'] = len(doc['genes'])
        yield doc