import mygene
import logging
from biothings.utils.dataload import dict_sweep, unlist


class IDLookup:
    """Query a list of IDs and scope against mygene.info.
    Attributes:
        species (str, int): Species common name or taxid.
        query_cache (dict, optional): Dictionary to store queries (keys)
            and results (values). Defaults to empty dictionary.
        ids (iterable): Array or set of ids to query by default.
        Todo: if scope is 'retired', make a note that original id is retired.
    """

    def __init__(self, species, cache_dict={}):
        self.species = species
        self.query_cache = cache_dict

    def query_mygene(self, ids, id_type):
        """Query information from mygene.info about each gene in 'ids'.
        Args:
            ids (iterable): Array or set of gene ids to query.
            id_type (str): query scope field for the ids.
                Can be a comma-separated string for multiple scopes.
                e.g. 'entrezgene,symbol'
        """
        self.ids = ids
        mg = mygene.MyGeneInfo()
        # Fields to query
        fields = "entrezgene,ensembl.gene,uniprot.Swiss-Prot,symbol,name"
        if id_type == "symbol":
            scopes = "symbol,alias"
        elif id_type == "entrezgene":
            scopes = "entrezgene,retired"
        else:
            scopes = id_type
        response = mg.querymany(ids,
                                scopes=scopes,
                                fields=fields,
                                species=self.species,
                                returnall=True)
        # Save failed queries
        self.missing = response['missing']
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
            self.query_cache[query] = gene

    def retry_failed_with_new_ids(self, new_ids, new_id_type):
        """Retry failed queries with a new set of ids.
        Only retries for ids that failed using 'self.query_mygene()'.
        Args:
            new_ids (iterable): is a list or set where the number of elements
                matches the length and order of self.ids.
            new_id_type (str): query scope for the new set of ids."""
        retry_list = []
        for e in self.missing:
            indices = [i for i, x in enumerate(self.ids) if x == e]
            retry_list = retry_list + [new_ids[i] for i in indices]
        retry_list = list(set(retry_list))
        logging.info("Retrying with ids: {}".format(retry_list))
        if len(retry_list) > 0:
            if len(retry_list) == 1 and retry_list[0] == "":
                logging.info("No ids to retry.")
                return
            self.query_mygene(retry_list, new_id_type)