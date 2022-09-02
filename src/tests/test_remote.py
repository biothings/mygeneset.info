
from biothings.tests.web import BiothingsWebTest


class MyGenesetWebTestBase(BiothingsWebTest):
    host = 'mygeneset.info'


class TestMyGenesetDataIntegrity(MyGenesetWebTestBase):

    # --------------
    # Query endpoint
    # --------------

    def test_query_default_fields(self):
        self.query(q='glucose')

    def test_query_field(self):
        self.query(q='genes.ncbigene:1017')

    def test_species_filter_blank_query(self):
        dog = self.query(species='9615')
        print(3, dog['hits'][0])
        assert dog['hits'][0]['taxid'] == "9615"

    def test_species_filter_plus_query(self):
        dog = self.query(q='glucose', species='9615')
        print(dog['hits'][0])
        assert dog['hits'][0]['taxid'] == "9615"

    def test_query_by_id(self):
        _id = "WP100"
        query = self.query(q=f"_id:{_id}")
        assert query['hits'][0]['_id'] == _id

    def test_query_by_name(self):
        kinase = self.query(q='name:kinase')
        assert 'kinase' in kinase['hits'][0]['name'].lower()

    def test_query_by_description(self):
        desc = self.query(q='description:cytosine deamination')
        assert 'cytosine' in desc['hits'][0]['description'].lower()
        assert 'deamination' in desc['hits'][0]['description'].lower()

    def test_query_by_source_go(self):
        go = self.query(q='source:go', fields='all')
        assert 'go' in go['hits'][0].keys()
        assert go['hits'][0]['source'] == 'go'

    def test_query_by_source_ctd(self):
        ctd = self.query(q='source:ctd', fields='all')
        assert 'ctd' in ctd['hits'][0].keys()
        assert ctd['hits'][0]['source'] == 'ctd'

    def test_query_by_source_msigdb(self):
        msigdb = self.query(q='source:msigdb', fields='all')
        assert 'msigdb' in msigdb['hits'][0].keys()
        assert msigdb['hits'][0]['source'] == 'msigdb'

    def test_query_by_source_kegg(self):
        kegg = self.query(q='source:kegg', fields='all')
        assert 'kegg' in kegg['hits'][0].keys()
        assert kegg['hits'][0]['source'] == 'kegg'

    def test_query_by_source_do(self):
        do = self.query(q='source:do', fields='all')
        assert 'do' in do['hits'][0].keys()
        assert do['hits'][0]['source'] == 'do'

    def test_query_by_source_reactome(self):
        reactome = self.query(q='source:reactome', fields='all')
        assert 'reactome' in reactome['hits'][0].keys()
        assert reactome['hits'][0]['source'] == 'reactome'

    def test_query_by_source_smpdb(self):
        smpdb = self.query(q='source:smpdb', fields='all')
        assert 'smpdb' in smpdb['hits'][0].keys()
        assert smpdb['hits'][0]['source'] == 'smpdb'

    # TODO: Add POST endpoint tests

    # -------------------
    # Annotation endpoint
    # -------------------

    def test_annotation_default_fields(self):
        geneset_id = "WP100"
        res = self.request("geneset/" + geneset_id).json()
        assert res['_id'] == geneset_id
        expected_fields = ['genes', 'name', 'source', 'taxid', 'is_public', 'wikipathways']
        for field in expected_fields:
            assert field in res.keys()
