def get_customized_mapping(cls):
    mapping = {
        "source": {
            "normalizer": "keyword_lowercase_normalizer",
            "type": "keyword"
        },
        "taxid": {
            "type": "integer"
        },
        "count": {
            "type": "integer"
        },
        "metabolites_count": {
            "type": "integer"
        },
        "is_public": {
            "type": "boolean"
        },
        "smpdb": {
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
                "pw_id": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword",
                    "copy_to": [
                        "all"
                    ]
                },
                "pathway_subject": {
                    "type": "keyword"
                }
            }
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
        "metabolites": {
            "properties": {
                "mychem_id": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "smpdb_metabolite": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "hmdb": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "kegg_cid": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "chebi": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "drugbank": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "smiles": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "inchi": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "inchikey": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "pubchem": {
                    "type": "integer"
                },
                "chembl": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "cas": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "name": {
                    "type": "text"
                },
                "iupac": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                }
            }
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
        }
    }

    return mapping
