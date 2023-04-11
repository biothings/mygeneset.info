def get_customized_mapping(cls):
    mapping = {
        "name": {"type": "text", "copy_to": ["all"]},
        "is_public": {"type": "boolean"},
        "taxid": {"type": "integer"},
        "count": {"type": "integer"},
        "genes": {
            "properties": {
                "mygene_id": {"normalizer": "keyword_lowercase_normalizer", "type": "keyword"},
                "source_id": {"normalizer": "keyword_lowercase_normalizer", "type": "keyword"},
                "symbol": {"normalizer": "keyword_lowercase_normalizer", "type": "keyword"},
                "ncbigene": {"normalizer": "keyword_lowercase_normalizer", "type": "keyword"},
                "ensemblgene": {"normalizer": "keyword_lowercase_normalizer", "type": "keyword"},
                "uniprot": {"normalizer": "keyword_lowercase_normalizer", "type": "keyword"},
                "name": {"type": "text"},
                "taxid": {"type": "integer"},
            }
        },
        "duplicates": {
            "properties": {
                "ids": {
                    "properties": {
                        "id": {"normalizer": "keyword_lowercase_normalizer", "type": "keyword"},
                        "count": {"type": "integer"},
                    }
                },
                "count": {"type": "integer"},
            }
        },
        "not_found": {
            "properties": {
                "ids": {"normalizer": "keyword_lowercase_normalizer", "type": "keyword"},
                "count": {"type": "integer"},
            }
        },
        "reactome": {
            "properties": {
                "id": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword",
                    "copy_to": ["all"],
                },
                "geneset_name": {"type": "text"},
            }
        },
    }

    return mapping
