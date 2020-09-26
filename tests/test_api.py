from easy_entrez import EntrezAPI


entrez_api = EntrezAPI(
    'easy-entrez-test',
    'krassowski.michal+easyentrez@mail.com',
    return_type='json',
    # full 1 second interval as these tests are less urgent than any actual research
    minimal_interval=1
)


def test_search():
    result = entrez_api.search('cancer AND human[organism]', max_results=1)
    assert result.data['esearchresult']['count'] != 0
