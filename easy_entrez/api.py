import requests
from requests import Response
from typing import Dict, List
from xml.etree import ElementTree
from copy import copy
from time import time, sleep

from .batch import support_batches
from .types import ReturnType, DataType, EntrezDatabaseType, CommandType
from .queries import EntrezQuery, SearchQuery, SummaryQuery, FetchQuery, LinkQuery


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
        return_type: ReturnType = 'json',
        minimal_interval: int = 1 / 3,
        timeout: int = 10
    ):
        """
        Args:
            minimal_interval: the time interval (seconds) to be enforced between consecutive requests;
              by default 1/3 of a second to comply with the Entrez guidelines,
              but you may increase it if you want to be kind to others,
              or decrease it if you have an API key with an appropriate consent from Entrez.
        """
        self.tool = tool
        self.email = email
        self.api_key = api_key
        self.return_type = return_type
        self.minimal_interval = minimal_interval
        self._batch_size: int = None
        self._batch_sleep_interval: int = 3
        self._last_request_time = None
        self.timeout = timeout

    def _base_params(self) -> Dict[str, str]:
        return {
            'tool': self.tool,
            'email': self.email,
            'api_key': self.api_key,
            'retmode': self.return_type
        }

    def _request(self, query: EntrezQuery, custom_payload=None) -> EntrezResponse:
        url = f'{self.server}{query.endpoint_uri}'

        base_params = self._base_params()
        query_params = query.to_params()

        data = {
            # TODO maybe warn if overwriting?
            **base_params,
            **query_params,
            **(custom_payload or {})
        }

        current_time = time()
        if self._last_request_time is not None:
            elapsed = current_time - self._last_request_time
            if elapsed < self.minimal_interval:
                to_wait = self.minimal_interval - elapsed
                sleep(to_wait)
        self._last_request_time = current_time

        if query.method == 'get':
            response = requests.get(url, params=data, timeout=self.timeout)
        elif query.method == 'post':
            response = requests.post(url, data=data, timeout=self.timeout)
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

    def in_batches_of(self, size: int = 100, sleep_interval: int = 3):
        batch_mode = copy(self)
        batch_mode._batch_size = size
        batch_mode._batch_sleep_interval = sleep_interval
        return batch_mode

    @support_batches
    def summarize(
        self, ids: List[str], max_results: int,
        database: EntrezDatabaseType = 'pubmed'
    ):
        query = SummaryQuery(ids=ids, max_results=max_results, database=database)
        return self._request(query=query)

    @support_batches
    def fetch(
        self, ids: List[str], max_results: int,
        database: EntrezDatabaseType = 'pubmed', return_type: ReturnType = 'xml'
    ):
        query = FetchQuery(ids=ids, max_results=max_results, database=database, return_type=return_type)
        return self._request(query=query)

    @support_batches
    def link(
        self,
        # required
        ids: List[str],
        database_to: EntrezDatabaseType,
        database_from: EntrezDatabaseType,
        # optional
        command: CommandType = 'neighbor'
    ):
        query = LinkQuery(
            ids=ids, database=database_to, database_from=database_from,
            command=command
        )
        return self._request(query=query)
