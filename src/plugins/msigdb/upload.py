import glob
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
        xmlfiles = glob.glob(os.path.join(data_folder, "msigdb_v*.xml"))
        assert len(xmlfiles) == 1, "Expected one XML file in data folder"
        input_file = xmlfiles[0]
        docs = parse_msigdb(input_file)
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
                        "type": "text",
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
