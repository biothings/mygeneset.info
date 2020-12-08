import mygene


class IDLookup:
    def __init__(self, species, cache_dict={}):
        self.species = species
        self.query_cache = cache_dict

    def query_mygene(self, ids, id_type):
        """Query information from mygene.info about each gene in 'ids'."""
        # TO DO: if scope is 'retired', make a note that original id is retired.
        self.ids = ids
        mg = mygene.MyGeneInfo()
        # Fields to query
        fields = "entrezgene,ensembl.gene,uniprot.Swiss-Prot,symbol,name,locus_tag"
        response = mg.querymany(ids,
                                scopes=id_type,
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
                gene['symbol'] = out['symbol'],
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
            if out.get('locus_tag') is not None:
                gene['locus_tag'] = out['locus_tag']
            self.query_cache[query] = gene

    def retry_failed_with_new_ids(self, new_ids, new_id_type):
        """Retry failed queries with a new set of ids.
        new_ids is a list where elements match the length and order
        of self.ids"""
        id_map = {i: j for i, j in zip(self.ids, new_ids)}
        retry_list = [id_map[e] for e in self.missing]
        self.query_mygene(retry_list, new_id_type)
        mg = mygene.MyGeneInfo()
