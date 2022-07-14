import os

import biothings.hub.dataload.uploader as uploader

from .parser import parse_msigdb


class msigdbUploader(uploader.BaseSourceUploader):

    name = "msigdb"
    __metadata__ = {
        "src_meta": {
            'license_url': 'https://www.gsea-msigdb.org/gsea/msigdb_license_terms.jsp',
            'licence': 'CC Attribution 4.0 International',
            'url': 'https://www.gsea-msigdb.org/gsea/index.jsp'
        },
        "mapper": "count_genes"
    }

    def load_data(self, data_folder):
        """Load data from data folder"""
        data_file = os.path.join(data_folder, "msigdb_sorted.xml")
        assert os.path.exists(data_file), "Could not find 'msigdb_sorted.xml in data folder."
        docs = parse_msigdb(data_file)
        return docs

    @classmethod
    def get_mapping(cls):
        mapping = {
            "is_public": {
                "type": "boolean"
            },
            "taxid": {
                "type": "integer"
            },
            "name": {
                "type": "text",
                "copy_to": [
                    "all"
                ]
            },
            "description": {
                "type": "text",
                "copy_to": [
                    "all"
                ]
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
            "duplicates": {
                "properties": {
                    "dups": {
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
                        "type": "text",
                    },
                    "systematic_name": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "category_code": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "subcategory_code": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "authors": {
                        "type": "text"
                    },
                    "contributor": {
                        "type": "text"
                    },
                    "contributor_org": {
                        "type": "text"
                    },
                    "source": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "source_identifier": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "abstract": {
                        "type": "text",
                        "copy_to": [
                            "all"
                        ]
                    },
                    "pmid": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "geo_id": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "url": {
                        "properties": {
                            "geneset_listing": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "external_details": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    }
                }
            }
        }
        return mapping
