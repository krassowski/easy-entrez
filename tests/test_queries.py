"""
Testing against examples from https://www.ncbi.nlm.nih.gov/books/NBK25499/
"""
import pytest

import easy_entrez.data
from easy_entrez import queries
from easy_entrez.queries import EXAMPLES
from easy_entrez.types import Example


def test_codes():
    assert isinstance(easy_entrez.data.entrez_database_codes, list)
    assert 'pubmed' in easy_entrez.data.entrez_database_codes


@pytest.mark.parametrize('example', EXAMPLES[queries.LinkQuery])
def test_link_query(example: Example):
    assert example.query.full_uri() == example.uri


@pytest.mark.parametrize('example', EXAMPLES[queries.SearchQuery])
def test_search_query(example: Example):
    assert example.query.full_uri() == example.uri


@pytest.mark.parametrize('example', EXAMPLES[queries.CitationQuery])
def test_citation_query(example: Example):
    assert example.query.full_uri() == example.uri
