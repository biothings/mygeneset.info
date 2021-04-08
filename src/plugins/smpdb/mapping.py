def get_customized_mapping(cls):
    mapping = {
	"source": {
	    "normalizer": "keyword_lowercase_normalizer",
	    "type": "keyword"
	},
	"taxid": {
	    "type": "integer"
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
		    "type": "keyword"
		    "normalizer": "keyword_lowercase_normalizer",
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
