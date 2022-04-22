# MyGeneset Web Endpoints

## Login/Authentication

- `/login/github` Login with GitHub
- `/login/orcid` Login with ORCID
- `/logout` Clear user cookie
- `/user_info` Get user metadata

## User Genesets

### Create Genesets

**POST /user_geneset**

Arguments: 

- **dry_run:** Preview response without modifying any documents 

Body parameters:

- **name:** geneset name (required)
- **genes:** List of MyGene primary ids (required, can be an empty list)
- **is_public:** True/False (required)
- **description:** (optional)

Example requests:

```bash
# Create a public geneset (dryrun)

POST 'mygeneset.info/v1/user_geneset?dry_run=true' \
--header 'Content-Type: application/json' \
--data-raw '{
    "name" : "Test public geneset",
    "genes": ["1001", "1002"],
    "is_public": True,
    "description": "This is a public geneset"
}'


# Create a private geneset, (no dryrun) 

POST 'mygeneset.info/v1/user_geneset' \
--header 'Content-Type: application/json' \
--data-raw '{
    "name" : "Test private geneset",
    "genes": ["1001", "1002"],
    "is_public": False,
    "description": "This is a private geneset"
}'
```

### Update Genesets

**PUT /user_geneset/{geneset_id}**

Arguments: 

- **gene_operation:** What to do with the list of genes. Either 'replace', 'remove', or 'add'
- **dry_run:** Preview response without modifying any documents 

Body parameters:

- **name:** geneset name (optional, cannot be an empty string)
- **genes:** List of MyGene primary ids to add/remove/replace (optional)
- **is_public:** Boolean flag (optional)
- **description:** (optional)

Example requests:

```bash
# Rename a geneset:
PUT 'mygeneset.info0/v1/user_geneset/fdqOFX0B5sTLbCPOWILY'
--header 'Content-Type: application/json' \
--data-raw '{
    "name": "Test renamed geneset"
}
'

# Replace all genes (dry_run)
PUT 'mygeneset.info0/v1/user_geneset/fdqOFX0B5sTLbCPOWILY?gene_operation=replace&dry_run=true' \
--header 'Content-Type: application/json' \
--data-raw '{
    "is_public" : "True",
    "genes": ["14", "15"]
}
'

# Add new genes to geneset
PUT 'mygeneset.info0/v1/user_geneset/fdqOFX0B5sTLbCPOWILY?gene_operation=add' \
--header 'Content-Type: application/json' \
--data-raw '{
    "genes": ["15"]
}
'

# Remove genes from geneset
PUT 'mygeneset.info0/v1/user_geneset/fdqOFX0B5sTLbCPOWILY?gene_operation=remove' \
--header 'Content-Type: application/json' \
--data-raw '{
    "genes": ["14", "15"]
}
'
```

### Delete Genesets

**DELETE /user_geneset/{geneset_id}**

Arguments: 

- **dry_run:** Preview response without modifying any documents 

```bash
DELETE 'mygeneset.info/v1/user_geneset/4MUTmnwB04_PHShjT_C3'

# With dry_run
DELETE 'mygeneset.info/v1/user_geneset/4MUTmnwB04_PHShjT_C3&dry_run=true'
```
