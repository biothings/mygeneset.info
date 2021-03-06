#!/usr/bin/env python3

import json
import os
import re
import sys

import mygene
from biothings.utils.dataload import dict_sweep, unlist

try:                         # run as a data plugin module of Biothings SDK
    from biothings import config
    logging = config.logger
except Exception:            # run locally as a standalone script
    import logging
    LOG_LEVEL=logging.WARNING
    logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s: %(message)s')

TAX_ID = 9606  # Taxonomy ID of human being

# Varibles when searching MIM Disease ID from "Phenotypes" column in "genemap2.txt"
FIND_MIMID = re.compile('\, [0-9]* \([1-4]\)')  # Regex pattern
PHENOTYPE_FILTER = '(3)'

# Based on `go` class in "annotation-refinery/go.py".
# See https://github.com/greenelab/annotation-refinery
class GO:
    heads = None
    alt_id2std_id = None
    populated = None
    s_orgs = None

    # populate this field if you want to mark this GO as organism specific
    go_organism_tax_id = None

    def __init__(self):
        """
        Initialize data structures for storing the tree.
        """
        self.heads = []
        self.go_terms = {}
        self.alt_id2std_id = {}
        self.populated = False
        self.s_orgs = []

    def load_obo(self, path):
        """Load obo from the defined location. """
        obo_fh = None
        try:
            obo_fh = open(path)
        except IOError:
            logging.error('Could not open %s on the local filesystem.', path)

        if obo_fh is None:
            logging.error('Could not open %s.', path)
            return False

        self.parse(obo_fh)
        obo_fh.close()
        return True

    def parse(self, obo_fh):
        """
        Parse the passed obo handle.
        """
        inside = False
        gterm = None
        for line in obo_fh:
            fields = line.rstrip().split()

            if len(fields) < 1:
                continue
            elif fields[0] == '[Term]':
                if gterm:
                    if gterm.head:
                        self.heads.append(gterm)
                inside = True
            elif fields[0] == '[Typedef]':
                if gterm:
                    if gterm.head:
                        self.heads.append(gterm)
                inside = False

            elif inside and fields[0] == 'id:':
                if fields[1] in self.go_terms:
                    #logging.debug("Term %s exists in GO()", fields[1])
                    gterm = self.go_terms[fields[1]]
                else:
                    #logging.debug("Adding term %s to GO()", fields[1])
                    gterm = GOTerm(fields[1])
                    self.go_terms[gterm.get_id()] = gterm
            elif inside and fields[0] == 'def:':
                desc = ' '.join(fields[1:])
                desc = desc.split('"')[1]
                gterm.description = desc
            elif inside and fields[0] == 'name:':
                fields.pop(0)
                name = '_'.join(fields)
                name = re.sub('[^\w\s_-]', '_', name).strip().lower()
                name = re.sub('[-\s_]+', '_', name)
                gterm.name = name
                gterm.full_name = ' '.join(fields)
            elif inside and fields[0] == 'namespace:':
                gterm.namespace = fields[1]
            elif inside and fields[0] == 'def:':
                gterm.desc = ' '.join(fields[1:]).split('\"')[1]
            elif inside and fields[0] == 'alt_id:':
                gterm.alt_id.append(fields[1])
                self.alt_id2std_id[fields[1]] = gterm.get_id()
            elif inside and fields[0] == 'is_a:':
                #logging.debug("Making term.head for term %s = False", gterm)
                gterm.head = False
                fields.pop(0)
                pgo_id = fields.pop(0)
                if pgo_id not in self.go_terms:
                    self.go_terms[pgo_id] = GOTerm(pgo_id)

                gterm.is_a.append(self.go_terms[pgo_id])
                self.go_terms[pgo_id].parent_of.add(gterm)
                gterm.child_of.add(self.go_terms[pgo_id])
            elif inside and fields[0] == 'relationship:':
                if fields[1].find('has_part') != -1:
                    # Has part is not a parental relationship --
                    # it is actually for children.
                    continue
                #logging.debug("Making term.head for term %s = False", gterm)
                gterm.head = False
                pgo_id = fields[2]
                if pgo_id not in self.go_terms:
                    self.go_terms[pgo_id] = GOTerm(pgo_id)
                # Check which relationship you are with this parent go term
                if (fields[1] == 'regulates' or
                        fields[1] == 'positively_regulates' or
                        fields[1] == 'negatively_regulates'):
                    gterm.relationship_regulates.append(self.go_terms[pgo_id])
                elif fields[1] == 'part_of':
                    gterm.relationship_part_of.append(self.go_terms[pgo_id])
                else:
                    logging.info("Unkown relationship %s", self.go_terms[pgo_id].name)

                self.go_terms[pgo_id].parent_of.add(gterm)
                gterm.child_of.add(self.go_terms[pgo_id])
            elif inside and fields[0] == 'is_obsolete:':
                #logging.debug("Making term.head for term %s = False", gterm)
                gterm.head = False
                del self.go_terms[gterm.get_id()]

        # This loop checks that all terms that have been marked as head=True
        # have been added to self.heads
        for term_id, term in self.go_terms.items():
            if term.head:
                if term not in self.heads:
                    #logging.debug("Term %s not in self.heads, adding now", term)
                    self.heads.append(term)

        #logging.debug("Terms that are heads: %s", self.heads)

    def propagate(self):
        """
        propagate all gene annotations
        """
        logging.info("Propagate gene annotations")
        logging.debug("Head term(s) = %s", self.heads)
        for head_gterm in self.heads:
            logging.info("Propagating %s", head_gterm.name)
            self.propagate_recurse(head_gterm)

    def propagate_recurse(self, gterm):
        if not len(gterm.parent_of):
            #logging.debug("Base case with term %s", gterm.name)
            return

        for child_term in gterm.parent_of:
            self.propagate_recurse(child_term)
            new_annotations = set()

            regulates_relation = (gterm in child_term.relationship_regulates)
            part_of_relation = (gterm in child_term.relationship_part_of)

            for annotation in child_term.annotations:
                copied_annotation = None
                # If this relation with child is a regulates(and its sub class)
                # filter annotations
                if regulates_relation:
                    # only add annotations that didn't come from a part of or
                    # regulates relationship
                    if annotation.ready_regulates_cutoff:
                        continue
                    else:
                        copied_annotation = annotation.prop_copy(
                            ready_regulates_cutoff=True)
                elif part_of_relation:
                    copied_annotation = annotation.prop_copy(
                        ready_regulates_cutoff=True)
                else:
                    copied_annotation = annotation.prop_copy()

                new_annotations.add(copied_annotation)
            gterm.annotations = gterm.annotations | new_annotations

    def get_term(self, tid):
        #logging.debug('get_term: %s', tid)
        term = None
        try:
            term = self.go_terms[tid]
        except KeyError:
            try:
                term = self.go_terms[self.alt_id2std_id[tid]]
            except KeyError:
                logging.error('Term name does not exist: %s', tid)
        return term


# Copied from "annotation-refinery/go.py".
# See https://github.com/greenelab/annotation-refinery
class Annotation(object):
    def __init__(self, xdb=None, gid=None, ref=None, evidence=None, date=None,
                 direct=False, cross_annotated=False, origin=None,
                 ortho_evidence=None, ready_regulates_cutoff=False):
        super(Annotation, self).__setattr__('xdb', xdb)
        super(Annotation, self).__setattr__('gid', gid)
        super(Annotation, self).__setattr__('ref', ref)
        super(Annotation, self).__setattr__('evidence', evidence)
        super(Annotation, self).__setattr__('date', date)
        super(Annotation, self).__setattr__('direct', direct)
        super(Annotation, self).__setattr__('cross_annotated', cross_annotated)
        super(Annotation, self).__setattr__('origin', origin)
        super(Annotation, self).__setattr__('ortho_evidence', ortho_evidence)
        super(Annotation, self).__setattr__('ready_regulates_cutoff',
                                            ready_regulates_cutoff)

    def prop_copy(self, ready_regulates_cutoff=None):
        if ready_regulates_cutoff is None:
            ready_regulates_cutoff = self.ready_regulates_cutoff

        return Annotation(xdb=self.xdb, gid=self.gid, ref=self.ref,
                          evidence=self.evidence, date=self.date, direct=False,
                          cross_annotated=False,
                          ortho_evidence=self.ortho_evidence,
                          ready_regulates_cutoff=ready_regulates_cutoff)

    def __hash__(self):
        return hash((self.xdb, self.gid, self.ref, self.evidence, self.date,
                     self.direct, self.cross_annotated, self.ortho_evidence,
                     self.ready_regulates_cutoff, self.origin))

    def __eq__(self, other):
        return (self.xdb, self.gid, self.ref, self.evidence, self.date,
                self.direct, self.cross_annotated, self.ortho_evidence,
                self.ready_regulates_cutoff, self.origin).__eq__((
                    other.xdb, other.gid, other.ref, other.evidence,
                    other.date, other.direct, other.cross_annotated,
                    other.ortho_evidence, other.ready_regulates_cutoff,
                    other.origin))

    def __setattr__(self, *args):
        raise TypeError("Attempt to modify immutable object.")
    __delattr__ = __setattr__


# Copied from "annotation-refinery/go.py".
# See https://github.com/greenelab/annotation-refinery
class GOTerm:
    go_id = ''
    is_a = None
    relationship = None
    parent_of = None
    child_of = None
    annotations = None
    alt_id = None
    namespace = ''
    included_in_all = None
    valid_go_term = None
    cross_annotated_genes = None
    head = None
    name = None
    full_name = None
    description = None
    base_counts = None
    counts = None
    summary = None
    desc = None
    votes = None

    def __init__(self, go_id):
        self.head = True
        self.go_id = go_id
        self.annotations = set([])
        self.cross_annotated_genes = set([])
        self.is_a = []
        self.relationship_regulates = []
        self.relationship_part_of = []
        self.parent_of = set()
        self.child_of = set()
        self.alt_id = []
        self.included_in_all = True
        self.valid_go_term = True
        self.name = None
        self.full_name = None
        self.description = None
        self.base_counts = None
        self.counts = None
        self.desc = None
        self.votes = set([])

    def __cmp__(self, other):
        return cmp(self.go_id, other.go_id)

    def __hash__(self):
        return(self.go_id.__hash__())

    def __repr__(self):
        return(self.go_id + ': ' + self.name)

    def get_id(self):
        return self.go_id

    def map_genes(self, id_name):
        mapped_annotations_set = set([])
        for annotation in self.annotations:
            mapped_genes = id_name.get(annotation.gid)
            if mapped_genes is None:
                logging.warning('No matching gene id: %s', annotation.gid)
                continue
            for mgene in mapped_genes:
                mapped_annotations_set.add(
                    Annotation(
                        xdb=None,
                        gid=mgene,
                        direct=annotation.direct,
                        ref=annotation.ref,
                        evidence=annotation.evidence,
                        date=annotation.date,
                        cross_annotated=annotation.cross_annotated
                    )
                )
        self.annotations = mapped_annotations_set

    def get_annotated_genes(self, include_cross_annotated=True):
        genes = []
        for annotation in self.annotations:
            if (not include_cross_annotated) and annotation.cross_annotated:
                continue
            genes.append(annotation.gid)
        return genes

    def add_annotation(
            self,
            gid,
            ref=None,
            cross_annotated=False,
            allow_duplicate_gid=True,
            origin=None,
            ortho_evidence=None
    ):
        if not allow_duplicate_gid:
            for annotated in self.annotations:
                if annotated.gid == gid:
                    return
        self.annotations.add(
            Annotation(
                gid=gid,
                ref=ref,
                cross_annotated=cross_annotated,
                origin=origin,
                ortho_evidence=ortho_evidence
            )
        )

    def get_annotation_size(self):
        return len(self.annotations)

    def get_namespace(self):
        return self.namespace


# Copied from "annotation-refinery/process_do.py"
# See https://github.com/greenelab/annotation-refinery
def build_doid_omim_dict(obo_filename):
    """
    Function to read in DO OBO file and build dictionary of DO terms
    from OBO file that have OMIM cross-reference IDs

    Arguments:
    obo_filename -- A string. Location of the DO OBO file to be read in.

    Returns:
    doid_omim_dict -- A dictionary of only the DO terms in the OBO file
    that have OMIM xrefs. The keys in the dictionary are DOIDs, and the
    values are sets of OMIM xref IDs.
    """
    obo_fh = open(obo_filename, 'r')
    doid_omim_dict = {}

    # This statement builds a list of the lines in the file and reverses
    # its order. This is because the list 'pop()' method pops out list
    # elements starting from the end. This way the lines will be read in
    # the following loop in order, from top to bottom of the file.
    obo_reversed_str_array = obo_fh.readlines()[::-1]

    while obo_reversed_str_array:  # Loop adapted from Dima @ Princeton
        line = obo_reversed_str_array.pop()
        line = line.strip()
        if line == '[Term]':
            while line != '' and obo_reversed_str_array:
                line = obo_reversed_str_array.pop()

                if line.startswith('id:'):
                    doid = re.search('DOID:[0-9]+', line)
                    if doid:
                        doid = doid.group(0)

                if line.startswith('xref: OMIM:'):
                    # If term has OMIM xref, get it and add it to the
                    # doid_omim_dict. Otherwise, ignore.
                    omim = re.search('[0-9]+', line).group(0)

                    if doid not in doid_omim_dict:
                        doid_omim_dict[doid] = set()
                    if omim not in doid_omim_dict[doid]:
                        doid_omim_dict[doid].add(omim)

    obo_fh.close()
    return doid_omim_dict


# Based on `MIMdisease` class in "annotation-refinery/process_do.py".
# See https://github.com/greenelab/annotation-refinery
class MIMdisease:
    def __init__(self):
        self.id = ''
        self.phenotype = ''  # Phenotype mapping method
        self.genes = []      # list of gene IDs


# Based on `build_mim_diseases_dict()` in "annotation-refinery/process_do.py".
# See https://github.com/greenelab/annotation-refinery
def build_mim_diseases_dict(genemap_filename):
    """
    Function to parse genemap file and build a dictionary of MIM
    diseases.

    Arguments:
    genemap_filename -- A string. Location of the genemap file to read in.

    Returns:
    mim_diseases -- A dictionary. The keys are MIM disease IDs, and the
    values are `MIMdisease` objects, defined by the class above.

    *N.B. MIM IDs are not all one type of object (unlike Entrez IDs,
    for example) - they can refer to phenotypes/diseases, genes, etc.
    """

    mim_diseases = {}

    genemap_fh = open(genemap_filename, 'r')
    for line in genemap_fh:  # Loop based on Dima's @ Princeton
        tokens = line.strip('\n').split('\t')

        try:
            mim_geneid = tokens[5].strip()
            entrez_id = tokens[9].strip()
            disorders = tokens[12].strip()
        except IndexError:
            continue

        # Skip line if disorders field is empty
        if disorders == '':
            continue

        # Log message for empty "Entrez Gene ID" column
        if entrez_id == '':
            #logging.info(f"Empty Entrez Gene ID for MIM Number {mim_geneid}")
            continue

        # Split disorders and handle them one by one
        disorders_list = disorders.split(';')
        for disorder in disorders_list:
            if '[' in disorder or '?' in disorder:
                continue

            # This next line returns a re Match object:
            # It will be None if no match is found.
            mim_info = re.search(FIND_MIMID, disorder)

            if mim_info:
                split_mim_info = mim_info.group(0).split(' ')
                mim_disease_id = split_mim_info[1].strip()
                mim_phenotype = split_mim_info[2].strip()

                # Check if the mim_phenotype number is the one
                # in our filter. If not, skip and continue
                if mim_phenotype != PHENOTYPE_FILTER:
                    continue

                if mim_disease_id not in mim_diseases:
                    mim_diseases[mim_disease_id] = MIMdisease()
                    mim_diseases[mim_disease_id].id = mim_disease_id
                    mim_diseases[mim_disease_id].phenotype = mim_phenotype

                if entrez_id not in mim_diseases[mim_disease_id].genes:
                    mim_diseases[mim_disease_id].genes.append(entrez_id)

    genemap_fh.close()
    return mim_diseases


# Based on `add_do_term_annotations()` in "annotation-refinery/process_do.py"
# See https://github.com/greenelab/annotation-refinery
def add_term_annotations(doid_omim_dict, disease_ontology, mim_diseases):
    """
    Function to add annotations to only the disease_ontology terms found in
    the doid_omim_dict (created by the build_doid_omim_dict() function).

    Arguments:
    doid_omim_dict -- Dictionary mapping DO IDs to OMIM xref IDs. Only DOIDs
    with existing OMIM xref IDs are present as keys in this dictionary.

    disease_ontology -- A Disease Ontology that has parsed the DO OBO file.
    This is actually just a GO object (see imports for this file) that
    has parsed a DO OBO file instead of a GO OBO file.

    mim_diseases -- Dictionary of MIM IDs as the keys and MIMdisease
    objects (defined above) as values.

    Returns:
    A set of Entrez gene IDs, which will be used in MyGene.info query.
    """

    #logging.debug(disease_ontology.go_terms)

    entrez_set = set()
    for doid in doid_omim_dict.keys():
        term = disease_ontology.get_term(doid)
        if term is None:
            continue

        #logging.info("Processing %s", term)

        omim_id_list = doid_omim_dict[doid]
        for omim_id in omim_id_list:
            # If omim_id is not in mim_diseases dict, ignore it.
            if omim_id not in mim_diseases:
                continue

            mim_entry = mim_diseases[omim_id]
            for gene_id in mim_entry.genes:
                entrez = int(gene_id)
                entrez_set.add(entrez)
                term.add_annotation(gid=entrez, ref=None)

    return entrez_set

# Based on `create_do_term_title()` in "annotation-refinery/process_do.py"
# See https://github.com/greenelab/annotation-refinery
def create_gs_id(do_term):
    """
    Small function to create the DO term title in the desired
    format: DO-<DO integer ID>:<DO term full name>
    Example: DO-9351:diabetes mellitus

    Arguments:
    do_term -- This is a GOTerm object

    Returns:
    title -- A string of the DO term's title in the desired format.
    """
    do_id = do_term.go_id
    do_num = do_id.split(':')[1]
    title = 'DO' + '-' + do_num + ':' + do_term.full_name

    return title


# Based on `create_do_term_bastract()` in "annotation-refinery/process_do.py".
# See https://github.com/greenelab/annotation-refinery
def create_gs_abstract(do_term, doid_omim_dict):
    """
    Function to create the DO term abstract in the desired
    format.

    Arguments:
    do_term -- This is a go_term object from `GO` class

    doid_omim_dict -- A dictionary of DO terms mapping to sets of OMIM xrefs.
    This is returned by the build_doid_omim_dict() function above.

    Returns:
    abstract -- A string of the DO term's abstract in the desired format.
    """
    omim_clause = ''

    doid = do_term.go_id
    if doid in doid_omim_dict:
        # `omim_list` is sorted to make return value reproducible.
        omim_list = sorted(list(doid_omim_dict[doid]))
    else:
        omim_list = []

    if len(omim_list):
        omim_clause = ' Annotations directly to this term are provided ' + \
                        'by the OMIM disease ID'  # Is that sentence right?

        if len(omim_list) == 1:
            omim_clause = omim_clause + ' ' + omim_list[0]
        else:
            omim_clause = omim_clause + 's ' + ', '.join(omim_list[:-1]) + \
                ' and ' + omim_list[-1]
        omim_clause = omim_clause + '.'

    abstract = ''

    if do_term.description:
        abstract += do_term.description

    else:
        logging.info("No OBO description for term %s", do_term)

    abstract += (
        ' Annotations from child terms in the disease ontology are'
        + ' propagated through transitive closure.'
        + omim_clause
    )

    #logging.info(abstract)
    return abstract


def query_mygene(entrez_set, tax_id):
    """Query MyGene.info to get detailed gene information."""

    q_genes = entrez_set
    q_scopes = ['entrezgene', 'retired']
    output_fields = ['entrezgene', 'ensembl.gene', 'symbol', 'uniprot']

    mg = mygene.MyGeneInfo()
    logging.info(f"Querying {q_scopes} in MyGene.info ...")
    q_results = mg.querymany(
        q_genes,
        scopes=q_scopes,
        fields=output_fields,
        species=tax_id,
        returnall=True
    )

    genes_info = dict()
    for gene in q_results['out']:
        q_str = gene["query"]

        # Ensembl gene ID
        ensembl_gene = None
        ensembl = gene.get('ensembl', None)
        if ensembl and 'gene' in ensembl:
            ensembl_gene =  ensembl['gene']

        # Only keep 'Swiss-Prot' component in 'uniprot'
        uniprot = gene.get('uniprot', None)
        if uniprot:
            uniprot = uniprot.get('Swiss-Prot', None)

        genes_info[q_str] = {
            'mygene_id': gene.get('_id', None),
            'ncbigene': gene.get('entrezgene', None),
            'ensemblgene': ensembl_gene,
            'symbol': gene.get('symbol', None),
            'uniprot': uniprot
        }

    return genes_info


# Based on `process_do_terms()` in "annotation-refinery/process_do.py".
# See https://github.com/greenelab/annotation-refinery
# Changed from a regular function to generator to work with Biothings SDK.
def get_genesets(obo_filename, genemap_filename):
    disease_ontology = GO()
    obo_is_loaded = disease_ontology.load_obo(obo_filename)

    if obo_is_loaded is False:
        logging.error('Failed to load OBO file.')

    doid_omim_dict = build_doid_omim_dict(obo_filename)

    mim_diseases = build_mim_diseases_dict(genemap_filename)

    entrez_set = add_term_annotations(
        doid_omim_dict,
        disease_ontology,
        mim_diseases
    )

    genes_info = query_mygene(entrez_set, TAX_ID)
    disease_ontology.populated = True
    disease_ontology.propagate()

    genesets = list()
    for term_id, term in disease_ontology.go_terms.items():
        # If a term includes anyvalid gene IDs, add it as a geneset.
        gid_set = set()
        for annotation in term.annotations:
            gid_set.add(annotation.gid)

        if gid_set:
            my_geneset = {}
            my_geneset['_id'] = create_gs_id(term)
            my_geneset['is_public'] = True
            my_geneset['taxid'] = TAX_ID

            # Genes in a geneset are sorted by their IDs to make output reproducible.
            my_geneset['genes'] = [genes_info[str(gid)] for gid in sorted(gid_set)]
            my_geneset['do'] = {
                'id': term_id,
                'abstract': create_gs_abstract(term, doid_omim_dict)
            }
            my_geneset = dict_sweep(my_geneset, vals=[None], remove_invalid_list=True)
            my_geneset = unlist(my_geneset)
            genesets.append(my_geneset)

    return genesets


def load_data(data_dir):
    """Simple generator for Biothings SDK."""

    obo_filename = os.path.join(data_dir, "HumanDO.obo")
    genemap_filename = os.path.join(data_dir, "genemap2.txt")

    genesets = get_genesets(obo_filename, genemap_filename)
    for gs in genesets:
        yield gs


# Test harness
if __name__ == "__main__":
    data_dir = "./data/latest"
    genesets = list(load_data(data_dir))
    for gs in genesets:
        print(json.dumps(gs, indent=2))

    print("\nTotal number of gs:", len(genesets))
