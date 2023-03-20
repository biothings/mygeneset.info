import logging
from collections import namedtuple

import mygene
from biothings.utils.dataload import dict_sweep, unlist
from requests.exceptions import HTTPError


class MyGeneLookup:
    """Query a list of IDs and scopes against mygene.info.
    Attributes:
        species (str, int): Species common name or taxid.
        query_cache (dict, optional): Dictionary to store queries (keys)
            and results (values). Defaults to empty dictionary.
        fields_to_query: List of fields to query. If changing this,
            you may want to reset the query_cache.
    Usage:
        Initialize with a list of ids and a species.

        >>> from biothings.utils.mygene_lookup import MyGeneLookup
        >>> ids = ["ENSG00000097007", "ENSG00000096968"]
        >>> taxid = 9606  # human
        >>> gene_lookup = MyGeneLookup(taxid)
        >>> gene_lookup.query_mygene(ids, "ensembl.gene")

        Or, provide a list of tuples and list of id types for retry:

        >>> ids = [("ABL1", "ENSG00000097007"), ("JAK2", "ENSG00000096968")]
        >>> taxid = 9606  # human
        >>> gene_lookup = MyGeneLookup(taxid)
        >>> gene_lookup.query_mygene(ids, ["symbol", "ensembl.gene"])

        Finally, get the search results:

        >>> geneset = {"_id": id, "name": geneset_name, "description": desc,
                       "is_public": is_public, "taxid": species, "source": source}
        >>> lookup_results = gene_lookup.get_results(ids)
        >>> geneset = geneset.update(lookup_results)
    """

    # Taxid mappings for commonly used species
    SPECIES_MAP = {
        "human": "9606",
        "mouse": "10090",
        "rat": "10116",
        "fruitfly": "7227",
        "nematode": "6239",
        "zebrafish": "7955",
        "thale-cress": "3702",
        "frog": "8364",
        "pig": "9823",
    }

    def __init__(self, species="all", cache_dict=None):
        """Species can be a single taxid, or a list of taxids, or comma separated string.
        e.g.: [9606, 10090] or '9606,10090'.
        To search against all species, use 'all' (default).
        """
        if (
            not isinstance(species, list)
            and not isinstance(species, str)
            and not isinstance(species, int)
        ):
            raise ValueError("Species must be a string, integer, or list.")
        self.species = self._normalize_species(species)
        self.clear_cache()
        if cache_dict:
            self._query_cache = cache_dict
        self.fields_to_query = [
            "entrezgene",
            "ensembl.gene",
            "uniprot.Swiss-Prot",
            "symbol",
            "name",
            "taxid",
        ]

    def _normalize_species(self, species):
        """Standarize the input for species search.
        Species should always be a strig or list of strings.
        """
        if isinstance(species, int):
            species = str(species)
        if isinstance(species, str):
            species = species.split(",")
        species = [self.SPECIES_MAP[s] if s in self.SPECIES_MAP else str(s) for s in species]
        if len(species) == 1:
            species = species[0]
        return species

    def clear_cache(self):
        """Clear the query cache."""
        self._query_cache = {}

    def query_mygene(self, ids, id_types):
        """Query information from mygene.info about each gene in 'ids'.
        Args:
            ids: List of genes or list of tuples of gene ids to query.
                If genes are tuples, query retries will be enabled.
            id_types: Query scope field(s) for the ids.
                Can be a comma-separated string for multiple scopes (single query).
                e.g. 'entrezgene,retired'
                Or a list of strings, to enable retries (multiple queries):
                ['symbol', 'entrezgene,retired']
                If it is a list, ids must be a list of tuples.
                To search all scopes, pass "all" as `id_types`.
        """
        # Some checks
        assert isinstance(ids, list), "ids must be a list."
        if isinstance(id_types, list):
            retry = True
        elif isinstance(id_types, str):
            retry = False
        else:
            raise TypeError("id_types must be a string or list")
        if len(ids) == 0:
            return self
        if retry:
            assert all(
                isinstance(i, tuple) for i in ids
            ), "To use retry, ids must be a list of tuples."
            assert all(
                len(i) == len(id_types) for i in ids
            ), "The size of each tuple must match the size of id_types."
            retry_times = len(id_types) - 1
        else:
            assert all(isinstance(i, str) for i in ids), "all ids must be strings."
            retry_times = 0
        failed_ids = []
        current_try = 0
        while current_try <= retry_times:
            # Remove ids that are already in the cache
            if retry:
                new_ids = [n for n in ids if n[current_try] not in self._query_cache]
            else:
                new_ids = [n for n in ids if n not in self._query_cache]
            diff = len(ids) - len(new_ids)
            assert diff >= 0, "This shouldn't have happened!"
            if diff > 0:
                logging.info(f"Found {diff} genes in query cache.")
            elif len(ids) == 0:
                continue
            ids = new_ids
            logging.info(f"Searching for {len(ids)} genes...")
            # Generate params for query
            if retry:
                to_query = [n[current_try] for n in ids]
                scopes = id_types[current_try]
            else:
                to_query = ids
                scopes = id_types
            # Querying a one element list causes an HTTP 400 error
            if len(to_query) == 1:
                to_query = to_query[0]
            # multispecies genesets support
            if isinstance(self.species, list):
                taxid_query = ",".join(self.species)
            else:
                taxid_query = self.species
            # Query mygene.info
            mg = mygene.MyGeneInfo()
            try:
                response = mg.querymany(
                    to_query,
                    scopes=scopes,
                    fields=self.fields_to_query,
                    species=taxid_query,
                    returnall=True,
                )
            except HTTPError as e:
                if e.response.status_code == 400:
                    current_try += 1
                    continue
                else:
                    raise
            # Format successful queries
            for out in response["out"]:
                query = out["query"]
                if out.get("notfound"):
                    continue
                gene = {"mygene_id": out["_id"], "source_id": query}
                if out.get("symbol") is not None:
                    gene["symbol"] = out["symbol"]
                if out.get("name") is not None:
                    gene["name"] = out["name"]
                if out.get("entrezgene") is not None:
                    gene["ncbigene"] = out["entrezgene"]
                if out.get("ensembl") is not None:
                    if len(out["ensembl"]) > 1:
                        for i in out["ensembl"]:
                            gene.setdefault("ensemblgene", []).append(i["gene"])
                    else:
                        gene["ensemblgene"] = out["ensembl"]["gene"]
                if out.get("uniprot") is not None:
                    gene["uniprot"] = out["uniprot"]["Swiss-Prot"]
                # Add extra fields to document
                for field in self.fields_to_query:
                    if field not in [
                        "entrezgene",
                        "ensembl.gene",
                        "uniprot.Swiss-Prot",
                        "symbol",
                        "name",
                    ]:
                        if out.get(field) is not None:
                            gene[field] = out[field]
                gene = unlist(gene)
                gene = dict_sweep(gene)
                # Store results in cache
                # Handle duplicate hits by appending to list
                if self._query_cache.get(query):
                    if isinstance(self._query_cache[query], list):
                        self._query_cache[query].append(gene)
                    else:
                        self._query_cache[query] = [self._query_cache[query], gene]
                else:
                    self._query_cache[query] = gene
            # Save failed queries
            failed_ids = response["missing"]
            if len(failed_ids) == 0:
                logging.info("No ids to retry.")
                return
            if retry and (current_try + 1 <= retry_times):
                ids = [n for n in ids if n[current_try] in failed_ids]
                assert len(ids) == len(failed_ids), "The length of these lists should match."
                logging.info(f"Retrying {len(ids)} genes.")
            else:
                logging.info(f"Could not find {len(failed_ids)} genes.")
            current_try += 1
        return self

    def query_mygene_homologs(self, ids, id_types, new_species, orig_species="all"):
        """Convert a list of gene ids to their homologs from `new_species` and
        store a dictionary of gene ids for each homolog gene in self._query_cache.
        The dictionary keys are the original species' gene ids.
        Args:
            ids: List of genes or list of tuples of gene ids to query.
                If genes are tuples, query retries will be enabled.
            id_types: Query scope field(s) for the ids.
                Can be a comma-separated string for multiple scopes (single query).
                e.g. 'entrezgene,retired'
                Or a list of strings, to enable retries (multiple queries):
                ['symbol', 'entrezgene,retired']
                If it is a list, ids must be a list of tuples.
                To search all scopes, pass "all" as `id_types`.
            old_species: taxid of the species to convert from.
            new_species: taxid of the species to convert to. Defaults to "all".
        """
        new_species = self._normalize_species(new_species)
        orig_species = self._normalize_species(orig_species)
        if new_species == "all":
            raise ValueError("Cannot convert to all species.")
        # Start a mygene search with fields_to_query set to ['taxid', 'homologene']
        self.species = orig_species
        self.fields_to_query = ["taxid", "homologene"]
        self.query_mygene(ids, id_types)
        # Get results and create a conversion mapping between original and homolog ids
        Mapping = namedtuple("Mapping", "original_gene_id homolog_gene_id")
        mappings = []
        results = self.get_results(ids)
        for result in results.get("genes", []):
            original_id = result["source_id"]
            if str(result["taxid"]) == new_species:
                # No conversion needed
                mappings.append(Mapping(original_id, result["mygene_id"]))
                logging.info(
                    f"{original_id} already belongs to {new_species}, no conversion needed."
                )
                continue
            if result.get("homologene") is not None:
                if not isinstance(result["homologene"]["genes"][0], list):
                    # If there is only one homolog, make it into a list, so we can iterate over it
                    # We may not need this case, because when a gene has a single homolog entry,
                    # it is usually a reference to itself (i.e. no conversion needed).
                    result["homologene"]["genes"] = [result["homologene"]["genes"]]
                found = False
                for homolog_taxid, homolog_gene in result["homologene"]["genes"]:
                    # Find the right homolog gene id and add it to the mapping
                    if str(homolog_taxid) == new_species:
                        mappings.append(Mapping(original_id, str(homolog_gene)))
                        found = True
                if not found:
                    logging.info(f"Could not find a homolog match for {original_id}.")
                else:
                    logging.info(f"{original_id} converted to {mappings[-1].homolog_gene_id}.")
            else:
                logging.info(f"No homologene field found for {original_id}.")
        if results.get("not_found"):
            logging.info(f"Could not find {results['not_found']['count']} genes.")
        if results.get("duplicates"):
            logging.info(f"Found {results['duplicates']['count']} duplicate genes.")
        # Run a new mygene query using the new homolog ids
        # We clear the cache because we have a new taxid and set of returned fields
        self.clear_cache()
        self.species = new_species
        self.fields_to_query = [
            "entrezgene",
            "ensembl.gene",
            "uniprot.Swiss-Prot",
            "symbol",
            "name",
            "taxid",
        ]
        new_ids = list(set([conversion.homolog_gene_id for conversion in mappings]))
        if len(new_ids) == 0:
            logging.info("No ids to query.")
        else:
            self.query_mygene(new_ids, "_id")
            # Edit _query_cache to make the original ids the dictionary key and the value of 'source_id'
            # TODO: This is a bit convoluted. We should probably create functions to handle editing the cache.
            for Mapping in mappings:
                if self._query_cache.get(Mapping.homolog_gene_id):
                    # Set the original gene id as the dictionary key
                    if isinstance(Mapping.original_gene_id, list):
                        # When the original gene id is a list, (i.e. there are two synonyms for the same gene),
                        # Make duplicates for each source id in Mapping.original_gene_id.
                        # This is necessary because you cannot use a list as a dictionary key.
                        # However, the duplicates should be eventually merged by get_results().
                        for source_id in Mapping.original_gene_id:
                            self._query_cache[source_id] = self._query_cache[
                                Mapping.homolog_gene_id
                            ].copy()
                            # Set each gene's 'source_id' field to the original gene id
                            if isinstance(self._query_cache[source_id], list):
                                # In the case of multiple homologs for the same species.
                                # e.g. one human gene correspongs to two mouse genes.
                                # I haven't found a case where this happens, but it is possible.
                                for i in self._query_cache[source_id]:
                                    i[
                                        "source_id"
                                    ] = source_id  # Merging during get_results() should recreate the list.
                            else:
                                self._query_cache[source_id]["source_id"] = source_id
                    else:
                        self._query_cache[Mapping.original_gene_id] = self._query_cache[
                            Mapping.homolog_gene_id
                        ].copy()
                        # Set each gene's 'source_id' field to the original gene id
                        if isinstance(self._query_cache[Mapping.original_gene_id], list):
                            # In the case of multiple homologs for the same species.
                            # e.g. one human gene correspongs to two mouse genes.
                            # I haven't found a case where this happens, but it is possible.
                            for i in self._query_cache[Mapping.original_gene_id]:
                                i["source_id"] = Mapping.original_gene_id
                        else:
                            self._query_cache[Mapping.original_gene_id][
                                "source_id"
                            ] = Mapping.original_gene_id
        return self

    def get_results(self, ids):
        """Generate a formatted geneset from lookup results for a list of ids.
        Args:
            ids: List of ids or id tuples to put in geneset.
        Returns:
            Dictionary containing taxid, genes, count, duplicates and failed ids.
            The schema for the returned dictionary is:
            {
                "genes": [
                    {
                     "mygene_id": "",
                     "source_id": "",
                     "symbol": "",
                     "name": "",
                     "ncbigene": "",
                     "ensemblgene": "",
                     "uniprot": "",
                     "taxid": ""      // if multispecies
                    }
                ],
                "count": 0,
                "duplicates": {
                    "ids": [
                        {
                         "id": "",
                         "count": 0
                        }
                    ],
                    "count": 0
                }
                "not_found": {
                    "ids": [],
                    "count": 0
                }
             }
        """
        genes = []
        missing = []
        dups = []
        assert isinstance(ids, list), "ids must be a list."
        # Force each element into tuples if it's not already
        for idx, elem in enumerate(ids):
            if not isinstance(elem, tuple):
                assert isinstance(elem, str), "All ids must be strings."
                ids[idx] = (elem,)
        # Make sure each element has the same length
        if len(ids) > 0:
            first_len = len(ids[0])
            assert all(
                len(elem) == first_len for elem in ids
            ), "All tuples must have the same length."
        # Check if any of the ids are in the cache, using the first element of the tuple as the key
        # If there are more than one element in the tuple, we use subsequent elements as retry attempts
        if len(ids) > 0:
            retry_count = len(ids[0])
        for q in ids:
            i = 0
            found = False
            while i < retry_count:
                if self._query_cache.get(q[i]):
                    if isinstance(self._query_cache[q[i]], list):
                        genes += self._query_cache[q[i]]
                        dups.append({"id": q[i], "count": len(self._query_cache[q[i]])})
                    else:
                        genes.append(self._query_cache[q[i]])
                    found = True
                    break
                i += 1
            if not found:
                # Add first element of tuple to missing list,
                # as the first element is usually the preferred id
                missing.append(q[0])
        # Check that the field mygene_id is unique in the geneset, and merge duplicates
        # (duplicates can be caused by cases such as two synonyms in the input gene list)
        #  TODO: I feel like this could be more cleanly implemented
        # Perhaps it should be a separate function?
        if len(genes) > 0:
            unique_documents = {}
            for doc in genes:
                if doc["mygene_id"] not in unique_documents:
                    unique_documents[doc["mygene_id"]] = doc
                else:
                    # Merge duplicate entries
                    new_source = doc["source_id"]
                    unique_sources = unique_documents[doc["mygene_id"]]["source_id"]
                    if isinstance(unique_sources, list):
                        if isinstance(new_source, list):
                            # Both are lists
                            for s in new_source:
                                if s not in unique_sources:
                                    unique_sources.append(s)
                        elif new_source not in unique_sources:
                            # Only unique_sources is a list
                            unique_sources.append(new_source)
                    else:
                        if new_source != unique_sources:
                            if isinstance(new_source, list):
                                # Only new_source is a list
                                for s in new_source:
                                    if s not in unique_sources:
                                        unique_sources = [unique_sources]
                                        unique_sources.append(s)
                            else:
                                # Neither is a list
                                unique_documents[doc["mygene_id"]]["source_id"] = [
                                    unique_sources,
                                    new_source,
                                ]
            genes = list(unique_documents.values())
        results = {}
        results["genes"] = genes
        results["count"] = len(genes)
        if len(dups) > 0:
            results["duplicates"] = {"ids": dups, "count": len(dups)}
        if len(missing) > 0:
            results["not_found"] = {"ids": missing, "count": len(missing)}
        return results
