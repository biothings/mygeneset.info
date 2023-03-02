import os
import pytest

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
        assert dog['hits'][0]['taxid'] == "9615"

    def test_species_filter_plus_query(self):
        dog = self.query(q='glucose', species='9615')
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

    @pytest.mark.skip(reason="We removed kegg data source for now")
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

    def test_include_filter_check(self):
        query_all = self.query(include='all')
        query_curated = self.query(include='curated')
        query_public = self.query(include='public')
        query_user = self.query(include='user')
        query_anonymous = self.query(include='anonymous')
        assert query_all['total'] == query_curated['total'] + query_user['total']
        assert query_all['total'] >= query_public['total']
        assert query_user['total'] >= query_anonymous['total']

    def test_include_all_filter_plus_query(self):
        query = self.query(q='glucose', species='9615', include='all')
        assert query['hits'][0]['taxid'] == "9615"

    def test_include_curated_filter_plus_query(self):
        query = self.query(q='glucose', species='9615', include='curated')
        assert query['hits'][0]['taxid'] == "9615"

    def test_include_public_filter_plus_query(self):
        query = self.query(q='glucose', species='9615', include='public')
        assert query['hits'][0]['taxid'] == "9615"

    def test_include_user_filter_plus_query(self):
        res = self.request("query?q=glucose&species=9615&include=user").json()
        assert res['total'] == 0
        assert len(res['hits']) == 0

    def test_include_anonymous_filter_plus_query(self):
        res = self.request("query?q=glucose&species=9615&include=anonymous").json()
        assert res['total'] == 0
        assert len(res['hits']) == 0

    def test_include_filter_error(self):
        with pytest.raises(AssertionError) as e:
            self.request("query?include=a_wrong_include")
        e_str = str(e)
        error_code = '"code":400'
        error_status = '"success":false'
        error_msg = '"error":"Bad Request"'
        error_keyword = '"keyword":"include"'
        error_allowed = '"allowed":["all","curated","public","user","anonymous"]'
        assert error_code in e_str
        assert error_status in e_str
        assert error_msg in e_str
        assert error_keyword in e_str
        assert error_allowed in e_str


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

    # -------------------
    # Metadata endpoint
    # -------------------

    def test_metadata(self):
        root_res = self.request('/metadata').json()
        api_res = self.request('metadata').json()
        assert root_res == api_res
        available_fields = {'build_version', 'build_date', 'stats', 'src', 'biothing_type'}
        assert root_res.keys() == available_fields
        stats_fields = {'total', 'curated', 'user', 'anonymous'}
        assert root_res['stats'].keys() == stats_fields
