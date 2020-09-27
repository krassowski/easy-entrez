import requests
from requests import Response
from typing import Dict, List, Optional
from xml.etree import ElementTree
from copy import copy
from time import time, sleep

from .batch import supports_batches
from .types import ReturnType, DataType, EntrezDatabase, CommandType, Citation
from .queries import (
    EntrezQuery, SearchQuery, SummaryQuery, FetchQuery, LinkQuery, InfoQuery, CitationQuery, uses_query,
)


class EntrezResponse:
    """The wrapper around the Entrez response."""

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
    """
    Parameters:
        tool: Name of application making the E-utility call. Value must be a string with no internal spaces.
        email: E-mail address of the E-utility user.
            Value must be a string with no internal spaces, and should be a valid e-mail address.
        api_key: Since December 2018, NCBI began enforcing the practice of using an API key
            for users that post more than 3 requests per second.
            Please see `Chapter 2 <https://www.ncbi.nlm.nih.gov/books/n/helpeutils/chapter2/>`_ for a full discussion of this policy.
        return_type: Retrieval type. Determines the format of the returned output.
        minimal_interval: The time interval (seconds) to be enforced between consecutive requests;
          by default slightly over 1/3 of a second to comply with the Entrez guidelines,
          but you may increase it if you want to be kind to others,
          or decrease it if you have an API key with an appropriate consent from Entrez.
        timeout: The timeout in seconds (default 10 seconds).
        server: The server address.
    """
    def __init__(
        self, tool: str, email: str, api_key=None,
        return_type: ReturnType = 'json',
        minimal_interval: float = 0.334,
        timeout: float = 10,
        server: str = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    ):
        self.server = server
        self.tool = tool
        self.email = email
        self.api_key = api_key
        self.return_type = return_type
        self.minimal_interval = minimal_interval
        self._batch_size: Optional[int] = None
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

    # TODO: make entrez response a generic and provide better typing of responses
    @uses_query(SearchQuery)
    def search(
        self, term: str, max_results: int,
        database: EntrezDatabase = 'pubmed', min_date=None, max_date=None
    ):
        assert not min_date and not max_date  # TODO
        query = SearchQuery(term=term, max_results=max_results, database=database)
        return self._request(query=query)

    def in_batches_of(self, size: int = 100, sleep_interval: int = 3):
        batch_mode = copy(self)
        batch_mode._batch_size = size
        batch_mode._batch_sleep_interval = sleep_interval
        return batch_mode

    @supports_batches
    @uses_query(SummaryQuery)
    def summarize(
        self, ids: List[str], max_results: int,
        database: EntrezDatabase = 'pubmed'
    ):
        query = SummaryQuery(ids=ids, max_results=max_results, database=database)
        return self._request(query=query)

    @supports_batches
    @uses_query(FetchQuery)
    def fetch(
        self, ids: List[str], max_results: int,
        database: EntrezDatabase = 'pubmed', return_type: ReturnType = 'xml'
    ):
        query = FetchQuery(ids=ids, max_results=max_results, database=database, return_type=return_type)
        return self._request(query=query)

    @supports_batches
    @uses_query(LinkQuery)
    def link(
        self,
        # required
        ids: List[str],
        database: EntrezDatabase,
        database_from: EntrezDatabase,
        # optional
        command: CommandType = 'neighbor'
    ):
        query = LinkQuery(
            ids=ids, database=database, database_from=database_from,
            command=command
        )
        return self._request(query=query)

    @uses_query(InfoQuery)
    def get_info(self, database: EntrezDatabase = None):
        query = InfoQuery(database=database)
        return self._request(query=query)

    @uses_query(CitationQuery)
    def find_citations(self, citations: List[Citation], database='pubmed'):
        query = CitationQuery(database=database, citations=citations)
        return self._request(query=query)
