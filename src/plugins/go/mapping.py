def get_customized_mapping(cls):
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
                "name": {
                    "type": "text"
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
                }
            }
        },
        "go": {
            "properties": {
                "id": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword",
                    "copy_to": [
                        "all"
                    ]
                },
                "url": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "type": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "definition": {
                    "type": "text"
                },
                "xrefs": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "contributing_genes": {
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
                "excluded_genes": {
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
                "colocalized_genes": {
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
                }
            }
        }
    }

    return mapping
