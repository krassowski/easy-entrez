"""
Testing against examples from https://www.ncbi.nlm.nih.gov/books/NBK25499/
"""
from easy_entrez import queries


def test_codes():
    assert isinstance(queries.entrez_database_codes, list)
    assert 'pubmed' in queries.entrez_database_codes


def test_link_query():

    # Example: Link from protein to gene
    # https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=protein&db=gene&id=15718680,157427902
    query = queries.LinkQuery(database_from='protein', database='gene', ids=[15718680, 157427902])
    assert query.full_uri() == 'elink.fcgi?db=gene&dbfrom=protein&id=15718680,157427902'

