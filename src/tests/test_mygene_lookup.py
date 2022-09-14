# Test MyGeneset utils

import os
import sys

import pytest

_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append("{}/..".format(_path))

from utils.mygene_lookup import MyGeneLookup


class TestMyGeneLookup:

    def test_001_geneset_with_one_gene_ensembl(self):
        genes = ['ENSG00000113141']
        taxid = "9606"
        lookup = MyGeneLookup(taxid)
        lookup.query_mygene(genes, 'ensembl.gene')
        results = lookup.get_results(genes)
        assert results['count'] == 1
        default_fields = [
            'mygene_id', 'source_id', 'symbol', 'name', 'ncbigene', 'ensemblgene', 'uniprot'
        ]
        for field in default_fields:
            assert field in results['genes'][0].keys(), "Field {} not found".format(field)
        assert results['genes'][0]['source_id'] == "ENSG00000113141"

    def test_002_geneset_with_two_gene_symbols(self):
        genes = ['ABL1', 'JAK2']
        taxid = "9606"
        lookup = MyGeneLookup(taxid)
        lookup.query_mygene(genes, 'symbol')
        results = lookup.get_results(genes)
        assert results['count'] == 2

    def test_003_geneset_with_duplicates(self):
        """One query ID maps to multiple genes."""
        genes = ['kinesin']
        taxid = "9606"
        lookup = MyGeneLookup(taxid)
        lookup.query_mygene(genes, 'name')
        results = lookup.get_results(genes)
        assert results['count'] > 1
        assert results['duplicates']

    def test_004_duplicates_many_to_one(self):
        """Many query IDs map to the same gene."""
        genes = ["Q9Y496", "11127", "KIF3A"]  # These three ids are synonyms
        lookup = MyGeneLookup("9606")
        lookup.query_mygene(genes, 'entrezgene,uniprot,symbol')
        results = lookup.get_results(genes)
        assert results['count'] == 1
        assert results['genes'][0]['source_id'] == ["Q9Y496", "11127", "KIF3A"]
        assert results['genes'][0]['mygene_id'] == "11127"

    def test_005_duplicates_identical_queries(self):
        identical_genes = ["Q9Y496", "Q9Y496", "Q9Y496"]
        gene_lookup = MyGeneLookup("9606")
        gene_lookup.query_mygene(identical_genes, 'uniprot')
        results = gene_lookup.get_results(identical_genes)
        assert results['count'] == 1
        assert results['genes'][0]['source_id'] == "Q9Y496"
        assert results['genes'][0]['mygene_id'] == "11127"

    def test_006_duplicates_identical_queries(self):
        identical_genes = ["ABL1", "ABL1", "ABL1"]
        gene_lookup = MyGeneLookup("9606")
        gene_lookup.query_mygene(identical_genes, 'symbol')
        results = gene_lookup.get_results(identical_genes)
        assert results['count'] == 1
        assert results['genes'][0]['source_id'] == "ABL1"
        assert results['genes'][0]['mygene_id'] == "25"

    def test_007_geneset_with_not_found(self):
        genes = ['dummy_id_1', 'dummy_id_2', 'dummy_id_3']
        taxid = "9606"
        lookup = MyGeneLookup(taxid)
        lookup.query_mygene(genes, 'entrezgene')
        results = lookup.get_results(genes)
        assert results['count'] == 0
        assert results['not_found']['count'] == 3

    def test_008_geneset_with_two_genes_and_retries(self):
        genes = [("dummy_id_1", "ENSG00000097007"), ("dummy_id_2", "dummy_id_3")]
        taxid = "9606"
        lookup = MyGeneLookup(taxid)
        lookup.query_mygene(genes, ['symbol', 'ensembl.gene'])
        results = lookup.get_results(genes)
        assert results['count'] == 1
        assert results['genes'][0]['source_id'] == "ENSG00000097007"

    def test_009_geneset_with_custom_fields(self):
        genes = ['23529']
        taxid = "9606"
        lookup = MyGeneLookup(taxid)
        lookup.fields_to_query = ['taxid', 'homologene']
        lookup.query_mygene(genes, 'entrezgene,retired')
        results = lookup.get_results(genes)
        assert results['count'] == 1
        for field in ['homologene', 'taxid']:
            assert field in results['genes'][0].keys(), "Field {} not found".format(field)

    def test_010_multispecies_geneset_string(self):
        genes = ["4734", "608738", "9913"]
        taxid = "9606,9615,507781"   # Taxids as string
        lookup = MyGeneLookup(taxid)
        lookup.query_mygene(genes, 'entrezgene')
        results = lookup.get_results(genes)
        assert results['count'] == 3
        for gene in results['genes']:
            assert "taxid" in gene.keys(), "Field taxid not found"

    def test_011_multispecies_geneset_list(self):
        genes = ["4734", "608738", "9913"]
        taxid = ["9606", "9615", "507781"]  # Taxids as list
        lookup = MyGeneLookup(taxid)
        lookup.query_mygene(genes, 'entrezgene')
        results = lookup.get_results(genes)
        assert results['count'] == 3
        for gene in results['genes']:
            assert "taxid" in gene.keys(), "Field taxid not found"

    def test_012_geneset_with_single_list_taxid(self):
        genes = ['ENSG00000113141']
        taxid = ["9606"]  # A single item list should still work
        lookup = MyGeneLookup(taxid)
        lookup.query_mygene(genes, 'ensembl.gene')
        results = lookup.get_results(genes)
        assert results['count'] == 1

    def test_021_geneset_with_integer_taxid(self):
        genes = ['ENSG00000113141']
        taxid = 9606
        lookup = MyGeneLookup(taxid)
        lookup.query_mygene(genes, 'ensembl.gene')
        results = lookup.get_results(genes)
        assert results['count'] == 1

    def test_022_geneset_with_integer_geneid(self):
        with pytest.raises(ValueError) as e:
            genes = [3550]
            taxid = "9606"
            lookup = MyGeneLookup(taxid)
            lookup.query_mygene(genes, 'entrezgene')
            lookup.get_results(genes)

    def test_023_geneset_with_integer_list_taxid(self):
        genes = ["3550", "100041503"]
        taxid = ["9606", "mouse"]
        lookup = MyGeneLookup(taxid)
        lookup.query_mygene(genes, 'entrezgene')
        results = lookup.get_results(genes)
        print(results)
        assert results['count'] == 2

    def test_030_homolog_convert_mouse_to_human(self):
        """Convert mouse genes to human genes"""
        mouse_to_human = [("98660", "477"), ("60594", "147968"), ("233115", "147991")]
        mousegenes = [g[0] for g in mouse_to_human]
        lookup = MyGeneLookup()
        lookup.query_mygene_homologs(mousegenes, "entrezgene", new_species="human", orig_species="mouse")
        results = lookup.get_results(mousegenes)
        assert results['count'] == 3
        assert [(g['source_id'], g['mygene_id'])for g in results['genes']] == mouse_to_human

    def test_031_homolog_convert_mouse_to_human_with_retries(self):
        """Convert mouse genes to human genes"""
        mousegenes = [("dummy_id_1", "98660"), ("dummy_id_2", "60594"), ("Q71B07", "dummy_id_3")]
        lookup = MyGeneLookup()
        id_types = ['uniprot', 'entrezgene']
        lookup.query_mygene_homologs(mousegenes, id_types, new_species="9606", orig_species="10090")
        results = lookup.get_results(mousegenes)
        assert results['count'] == 3
        assert [g['source_id'] for g in results['genes']] == ["98660", "60594", "Q71B07"]

    def test_032_homolog_convert_any_to_human(self):
        """Convert any genes to human genes"""
        any_to_human = [("711495", "148252"), ("507781", "4734"), ("530544", "147968")]
        original_genes = [g[0] for g in any_to_human]
        lookup = MyGeneLookup()
        lookup.query_mygene_homologs(original_genes, "entrezgene", new_species="human", orig_species="all")
        results = lookup.get_results(original_genes)
        assert results['count'] == 3
        assert [(g['source_id'], g['mygene_id']) for g in results['genes']] == any_to_human

    def test_033_homolog_convert_human_to_human(self):
        """Convert human genes to human genes"""
        human_to_human = [("447", "477"), ("147968", "147968")]
        genes = [g[0] for g in human_to_human]
        lookup = MyGeneLookup()
        lookup.query_mygene_homologs(genes, "entrezgene", new_species="9606", orig_species="all")
        results = lookup.get_results(genes)
        assert results['count'] == 2

    def test_034_homolog_convert_with_duplicates(self):
        """These two homolog genes correspond to the same human gene, but are in different species"""
        original_genes = ["711495", "780240"]
        lookup = MyGeneLookup()
        lookup.query_mygene_homologs(original_genes, "entrezgene", new_species="9606", orig_species="all")
        results = lookup.get_results(original_genes)
        assert results['count'] == 1
        assert results['genes'][0]['source_id'] == ["711495", "780240"]
        assert results['genes'][0]['mygene_id'] == "148252"

    def test_035_homolog_genes_not_found(self):
        """Try to convert genes that doesn't exist"""
        genes = ["dummy_id_1", "dummy_id_2"]
        lookup = MyGeneLookup()
        lookup.query_mygene_homologs(genes, "entrezgene", new_species="human", orig_species="all")
        results = lookup.get_results(genes)
        assert results['count'] == 0
        assert results['not_found']['count'] == 2

    def test_036_homolog_real_not_found(self):
        """ This taxid is a real gene that doesn't have homologs.
        It still has a homologene field, but it is a single record
        pointing to itself.
        """
        genes = ['691975']
        lookup = MyGeneLookup()
        lookup.query_mygene_homologs(genes, "entrezgene", new_species="9606")
        results = lookup.get_results(genes)
        assert results['count'] == 0
        assert results['not_found']['count'] == 1

    def test_037_homolog_multiple_duplicates(self):
        genes = ['3630', '16334', '3630', '16334']
        lookup = MyGeneLookup()
        lookup.query_mygene_homologs(genes, "entrezgene", new_species="10090")
        results = lookup.get_results(genes)
        assert results['count'] == 1
        assert results['genes'][0]['mygene_id'] == '16334'
        assert results['genes'][0]['source_id'] == ['3630', '16334']

    def test_038_homolog_multiple_duplicates_with_synonyms(self):
        """"Four genes that map to the same rat gene,
        First two genes are entrez homologs for human and mouse.
        last two genes are their uniprot synonyms"""
        genes = ['3630', '16334', 'P01308', 'P01326']
        lookup = MyGeneLookup()
        lookup.query_mygene_homologs(genes, "entrezgene,uniprot", new_species="mouse")
        results = lookup.get_results(genes)
        assert results['count'] == 1
        assert results['genes'][0]['mygene_id'] == '16334'
        assert results['genes'][0]['source_id'] == ['3630', '16334', 'P01308', 'P01326']

    def test_50_empty_gene_list(self):
        """Test empty gene list"""
        lookup = MyGeneLookup()
        lookup.query_mygene([], "entrezgene")
        results = lookup.get_results([])
        assert results['genes'] == []
        assert results['count'] == 0

    def test_51_empty_homolog_gene_list(self):
        """Empty gene list"""
        lookup = MyGeneLookup()
        lookup.query_mygene_homologs([], "entrezgene", new_species="human")
        results = lookup.get_results([])
        assert results['genes'] == []
        assert results['count'] == 0
