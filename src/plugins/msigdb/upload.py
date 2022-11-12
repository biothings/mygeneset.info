import os

import biothings.hub.dataload.storage as storage
import biothings.hub.dataload.uploader as uploader

from .parser import parse_msigdb


class msigdbUploader(uploader.BaseSourceUploader):

    name = "msigdb"
    # Ignore documents with duplicate _id
    storage_class = storage.IgnoreDuplicatedStorage
    
    __metadata__ = {
        "src_meta": {
            'license_url': 'https://www.gsea-msigdb.org/gsea/msigdb_license_terms.jsp',
            'licence': 'CC Attribution 4.0 International',
            'url': 'https://www.gsea-msigdb.org/gsea/index.jsp'
        }
    }

    def load_data(self, data_folder):
        """Load data from data folder"""
        human_data_file = os.path.join(data_folder, "human_genesets.xml")
        mouse_data_file = os.path.join(data_folder, "mouse_genesets.xml")
        for file in [human_data_file, mouse_data_file]:
            if not os.path.exists(file):
                raise FileNotFoundError("Missing data file: %s" % file)
        return parse_msigdb(data_folder)

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
                    "dataset": {
                        "normalizer": "keyword_lowercase_normalizer",
                        "type": "keyword"
                    },
                    "category": {
                        "properties": {
                            "code": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            },
                            "name": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
                    },
                    "subcategory": {
                       "properties": {
                            "code": {
                                "normalizer": "keyword_lowercase_normalizer",
                                "type": "keyword"
                            }
                        }
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
