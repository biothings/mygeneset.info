import logging
from urllib.error import HTTPError

import mygene
from biothings.utils.dataload import dict_sweep, unlist


class IDLookup:
    """Query a list of IDs and scope against mygene.info.
    Attributes:
        species (str, int): Species common name or taxid.
        query_cache (dict, optional): Dictionary to store queries (keys)
            and results (values). Defaults to empty dictionary.
        ids (iterable): Array or set of ids to query by default.
        missing (list): List of ids that failed to query.
        dups (list): List of ids that had multiple hits.

    Usage:
        Initialize with a list of ids and a species.

        >>> from biothings.utils.geneset_utils import IDLookup
        >>> ids = ["ENSG00000097007", "ENSG00000096968"]
        >>> taxid = 9606  # human
        >>> gene_lookup = IDLookup(taxid)
        >>> gene_lookup.query_mygene(ids, "ensembl.gene")

        Or, provide a list of tuples and list of id types for retry:

        >>> ids = [("ABL1", "ENSG00000097007"), ("JAK2", "ENSG00000096968")]
        >>> taxid = 9606  # human
        >>> gene_lookup = IDLookup(taxid)
        >>> gene_lookup.query_mygene(ids, ["symbol", "ensembl.gene"])

        Finally, search query cache for hits.

        >>> genes = []
        >>> for id in ids:
        >>>     if gene_lookup.query_cache.get(id):
        >>>         genes += gene_lookup.query_cache[id]
    """

    def __init__(self, species, cache_dict={}):
        self.species = species
        self.query_cache = cache_dict

    def query_mygene(self, ids, id_types):
        """Query information from mygene.info about each gene in 'ids'.
        Args:
            ids: Array or set of gene ids to query. If genes are tuples,
                the order is used to determine retry order.
            id_types: query scope field for the ids.
                Can be a comma-separated string for multiple scopes.
                e.g. 'entrezgene,symbol'
                Or a list of strings, to enable retries:
                ['symbol', 'entrezgene']
        To search all fields, pass "all" as the id_type.
        """
        # Some checks
        if isinstance(id_types, list):
            retry = True
        elif isinstance(id_types, str):
            retry = False
        else:
            raise TypeError("id_types must be a string or list")

        if retry:
            assert isinstance(ids[0], tuple), "To use retry, ids must be a list of tuples."
            assert len(ids[0]) == len(id_types), "The size of each tuple must match the size of id_types"
            retry_times = len(id_types) - 1
            for n in ids:
                assert isinstance(n, tuple), "To use retry, all ids must be tuples."
                assert len(n) == len(id_types), "All tuples must be the same size."
        else:
            retry_times = 0
        failed_ids = []
        current_try = 0
        while current_try <= retry_times:
            # Remove ids that already in the cache
            if retry:
                new_ids = [n for n in ids if n[current_try]
                           not in self.query_cache.keys()]
            else:
                new_ids = [n for n in ids if n not in self.query_cache.keys()]
            diff = len(ids) - len(new_ids)
            assert diff >= 0, "This shouldn't have happened!"
            if diff > 0:
                logging.info(f"Found {diff} genes in query cache.")
            ids = new_ids
            if len(ids) == 0:
                continue
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
            # Query mygene.info
            mg = mygene.MyGeneInfo()
            fields_to_query = "entrezgene,ensembl.gene,uniprot.Swiss-Prot,symbol,name"
            try:
                response = mg.querymany(to_query,
                                        scopes=scopes,
                                        fields=fields_to_query,
                                        species=self.species,
                                        returnall=True)
            except HTTPError as err:
                if err.code == 400:
                    continue
                else:
                    raise
            # Format successful queries
            for out in response['out']:
                query = out['query']
                if out.get('notfound'):
                    continue
                gene = {'mygene_id': out['_id']}
                if out.get('symbol') is not None:
                    gene['symbol'] = out['symbol']
                if out.get('name') is not None:
                    gene['name'] = out['name']
                if out.get('entrezgene') is not None:
                    gene['ncbigene'] = out['entrezgene']
                if out.get('ensembl') is not None:
                    if len(out['ensembl']) > 1:
                        for i in out['ensembl']:
                            gene.setdefault('ensemblgene', []).append(i['gene'])
                    else:
                        gene['ensemblgene'] = out['ensembl']['gene']
                if out.get('uniprot') is not None:
                    gene['uniprot'] = out['uniprot']['Swiss-Prot']
                gene = dict_sweep(gene)
                gene = unlist(gene)
                # Store results in cache
                # Handle duplicate hits by appending to list
                if self.query_cache.get(query):
                    if isinstance(self.query_cache[query], list):
                        self.query_cache[query].append(gene)
                    else:
                        self.query_cache[query] = [self.query_cache[query], gene]
                else:
                    self.query_cache[query] = gene
            # Save failed queries
            failed_ids = response['missing']
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
