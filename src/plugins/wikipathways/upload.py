import biothings.hub.dataload.uploader as uploader
from .parser import load_data


class WikiPathwaysUploader(uploader.BaseSourceUploader):

    name = "wikipathways"
    __metadata__ = {
        "src_meta": {
            'license_url': 'https://www.wikipathways.org/index.php/WikiPathways:License_Terms',
            'licence': 'CC0 1.0 Universal',
            'url': 'https://www.wikipathways.org/'
            }
        }

    def load_data(self, data_folder):
        self.logger.info("Load data from folder '%s'" % data_folder)
        wikipathways_docs = load_data(data_folder)
        return wikipathways_docs

    @classmethod
    def get_mapping(cls):
        mapping = {
            "name": {
                "type": "text",
                "copy_to": [
                    "all"
                ]
            },
            "is_public": {
                "type": "boolean"
            },
            "taxid": {
                "type": "integer"
            },
            "count": {
                "type": "integer"
            },
            "genes": {
                "properties": {
                    "mygene_id": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "source_id": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "symbol": {
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
                    "locus_tag": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "name": {
                        "type": "text"
                    },
                    "taxid": {
                        "type": "integer"
                    }
                }
            },
            "duplicates": {
                "properties": {
                    "ids": {
                        "properties": {
                            "id": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "count": {
                                "type": "integer"
                            }
                        }
                    },
                    "count": {
                        "type": "integer"
                    }
                }
            },
            "not_found": {
                "properties": {
                    "ids": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "count": {
                        "type": "integer"
                    }
                }
            },
            "wikipathways": {
                "properties": {
                    "id": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword",
                        "copy_to": [
                            "all"
                        ]
                    },
                    "pathway_name": {
                        "type": "text"
                    },
                    "url": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    }
                }
            }
        }
        return mapping
