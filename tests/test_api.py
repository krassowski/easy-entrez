from pytest import raises
from easy_entrez import EntrezAPI
from easy_entrez.api import _match_all


entrez_api = EntrezAPI(
    'easy-entrez-test',
    'krassowski.michal+easyentrez@mail.com',
    return_type='json',
    # 2 seconds interval as these tests are less urgent than any actual research
    minimal_interval=2
)


def test_query_helpers():
    assert (
        _match_all(chromosome=13, organism='human', position=31873085)
        ==
        '13[chromosome] AND human[organism] AND 31873085[position]'
    )


def test_search():
    result = entrez_api.search('cancer AND human[organism]', max_results=1)
    assert result.data['esearchresult']['count'] != 0


def test_fetch():
    result = entrez_api.fetch(['4'], max_results=1, database='snp')
    snp = result.data[0]
    namespaces = {'ns0': 'https://www.ncbi.nlm.nih.gov/SNP/docsum'}
    chromosome = snp.find('.//ns0:CHR', namespaces).text
    assert chromosome == '13'

    with raises(ValueError, match='Received str but a list-like container of identifiers was expected'):
        entrez_api.fetch('4', max_results=1, database='snp')
