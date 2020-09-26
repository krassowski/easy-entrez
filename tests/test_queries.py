from easy_entrez import queries


def test_codes():
    assert isinstance(queries.entrez_database_codes, list)
    assert 'pubmed' in queries.entrez_database_codes

