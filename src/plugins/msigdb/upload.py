import biothings.hub.dataload.uploader as uploader
from .parser import load_data


class msigdbUploader(uploader.BaseSourceUploader):

    name = "msigdb"
    __metadata__ = {
        "src_meta": {
            'license_url': 'https://www.gsea-msigdb.org/gsea/msigdb_license_terms.jsp',
            'licence': 'CC Attribution 4.0 International',
            'url': 'https://www.gsea-msigdb.org/gsea/index.jsp'
            }
        }

    def load_data(self, data_folder):
        self.logger.info("Load data from folder '%s'" % data_folder)
        msigdb_docs = load_data(data_folder)
        return msigdb_docs


    @clasmethod
    def get_mapping(cls):
        mapping = {
            "is_public": {
                "type": "boolean"
            },
            "taxid": {
                "type": "integer"
            },
            "genes": {
                "properties": {
                    "mygene_id": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "symbol": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "ncbigene": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "ensemblgene": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "uniprot": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "name": {
                        "type": "text"
                    }
                }
            },
            "msigdb": {
                "properties": {
                    "id": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                        "copy_to": [
                            "all"
                        ]
                    },
                    "geneset_name": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                        "copy_to": [
                            "all"
                        ]
                    },
                    "url": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    }
                }
            }
        }
        return mapping
