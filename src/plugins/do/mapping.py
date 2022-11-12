def get_customized_mapping(cls):
    mapping = {
        "is_public": {
            "type": "boolean"
        },
        "taxid": {
            "type": "integer"
        },
        "count": {
            "type": "integer"
        },
        "source": {
            "normalizer": "keyword_lowercase_normalizer",
            "type": "keyword"
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
                "source_id": {
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
        "do": {
            "properties": {
                "id": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword",
                    "copy_to": [
                        "all"
                    ]
                },
                "abstract": {
                    "type": "text"
                }
            }
        }
    }

    return mapping
