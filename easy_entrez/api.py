import requests
from requests import Response
from typing import Dict, List
from xml.etree import ElementTree

from .types import ReturnType, DataType, EntrezDatabaseType
from .queries import EntrezQuery, SearchQuery, SummaryQuery, FetchQuery


class EntrezResponse:

    def __init__(self, query: EntrezQuery, response: Response, api: 'EntrezAPI'):
        self.query: EntrezQuery = query
        self.response: Response = response
        self.api: 'EntrezAPI' = api

    @property
    def content_type(self) -> ReturnType:
        declared_type = self.response.headers['Content-Type']
        if declared_type.startswith('application/json'):
            return 'json'
        if declared_type.startswith('text/xml'):
            return 'xml'
        raise ValueError(f'Unknown content type: {declared_type}')

    @property
    def data(self) -> DataType:
        if self.content_type == 'json':
            return self.response.json()
        if self.content_type == 'xml':
            return ElementTree.fromstring(self.response.content)
        raise ValueError(f'Unknown data data {self.content_type}')

    def __repr__(self):
        query = self.query
        response = self.response
        return f'<EntrezResponse status={response.status_code} for {query.summary}>'


class EntrezAPI:

    server = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'

    def __init__(
        self, tool: str, email: str, api_key=None,
        return_type: ReturnType ='json'
    ):
        self.tool = tool
        self.email = email
        self.api_key = api_key
        self.return_type = return_type

    def _base_params(self) -> Dict[str, str]:
        return {
            'tool': self.tool,
            'email': self.email,
            'api_key': self.api_key,
            'retmode': self.return_type
        }

    def _request(self, query: EntrezQuery, custom_payload=None):
        url = f'{self.server}{query.endpoint}{query.endpoint_suffix}'

        data = {
            # TODO maybe warn if overwriting?
            **self._base_params(),
            **query.to_params(),
            **(custom_payload or {})
        }

        if query.method == 'get':
            response = requests.get(url, params=data)
        elif query.method == 'post':
            response = requests.post(url, data=data)
        else:
            raise ValueError(f'Incorrect query method: {query.method}')

        return EntrezResponse(query=query, response=response, api=self)

    def search(
        self, term: str, max_results: int,
        database: EntrezDatabaseType = 'pubmed', min_date=None, max_date=None
    ):
        assert not min_date and not max_date  # TODO
        query = SearchQuery(term=term, max_results=max_results, database=database)
        return self._request(query=query)

    def summarize(
        self, ids: List[str], max_results: int,
        database: EntrezDatabaseType = 'pubmed'
    ):
        query = SummaryQuery(ids=ids, max_results=max_results, database=database)
        return self._request(query=query)

    def fetch(
        self, ids: List[str], max_results: int,
        database: EntrezDatabaseType = 'pubmed', return_type: ReturnType = 'xml'
    ):
        query = FetchQuery(ids=ids, max_results=max_results, database=database, return_type=return_type)
        return self._request(query=query)
