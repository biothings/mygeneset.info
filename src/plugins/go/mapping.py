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
                "symbol": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "name": {
                    "type": "text"
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
                "class": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "name": {
                    "type": "text"
                },
                "description": {
                    "type": "text"
                },
                "xrefs": {
                    "normalizer": "keyword_lowercase_normalizer",
                    "type": "keyword"
                },
                "contributing": {
                    "properties": {
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
                        "count": {
                            "type": "integer"
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
                        }
                    }
                },
                "colocalized": {
                    "properties": {
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
                        "count": {
                            "type": "integer"
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
                        }
                    }
                },
                "excluded": {
                    "properties": {
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
                        "count": {
                            "type": "integer"
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
                        }
                    }
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
        }
    }
    return mapping
