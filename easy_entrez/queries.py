from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Iterable, Type
from typing_extensions import Literal
from warnings import warn

from .types import ReturnType, EntrezDatabase, Command, Identifier, Example, Citation
from .data import entrez_databases, entrez_database_codes


@dataclass
class EntrezQuery(ABC):
    """
    Parameters:
        database: The database to query. Value must be a valid E-utility database name.
    """
    database: EntrezDatabase
    method = 'get'
    endpoint_suffix = '.fcgi'

    @property
    @abstractmethod
    def endpoint(self):
        """The name of the endpoint."""

    @property
    def endpoint_uri(self):
        return f'{self.endpoint}{self.endpoint_suffix}'

    def validate(self):
        if self.database not in entrez_database_codes and self.database is not None:
            warn(f'Unknown database: {self.database}')

    def __post_init__(self):
        self.validate()

    @property
    def uid_meaning(self):
        return entrez_databases

    def to_params(self) -> Dict[str, str]:
        # Convert to params which can be accepted by Entrez
        # TODO maybe use pydantic instead?
        params = {}
        if self.database:
            params['db'] = self.database
        return params

    @property
    def summary(self):
        return f'{self.__class__.__name__} in {self.database}'

    def full_uri(self):
        params = self.to_params()
        return self.endpoint_uri + '?' + '&'.join([f'{key}={value}' for key, value in params.items()])


@dataclass
class InfoQuery(EntrezQuery):
    """
    Functionality:
        - Provides a list of the names of all valid Entrez databases
        - Provides statistics for a single database, including lists of indexing fields and available link names

    Parameters:
        database: if not provided, will return a list of the names of all valid Entrez databases.
    """
    endpoint = 'einfo'


@dataclass
class SearchQuery(EntrezQuery):
    """
    Functionality:
        - Provides a list of UIDs matching a text query
        - Posts the results of a search on the History server
        - Downloads all UIDs from a dataset stored on the History server
        - Combines or limits UID datasets stored on the History server
        - Sorts sets of UIDs

    Parameters:
        database: Database to search.
            Value must be a valid E-utility database name (default = :py:obj:`'pubmed'`).
        term: Entrez text query
        max_results: Maximal number of results to return. Limited to 10'000, following
            the eUtils documentation.
        ignore_max_results_limit: Ignore the upper limit placed on max_results.
            Experimentation has shown that some databases allow for higher limits, but
            as this is not documented, setting higher limits needs to be explicitly
            enabled here. Use at your own risk of hard to predict errors.
    """
    endpoint = 'esearch'
    term: str
    max_results: int
    ignore_max_results_limit: bool = False

    def validate(self):
        super().validate()
        if self.max_results > 10_000 and not self.ignore_max_results_limit:
            raise ValueError('Fetching more than 10,000 results is not implemented')

    def to_params(self) -> Dict[str, str]:
        params = super().to_params()
        params['retmax'] = str(self.max_results)
        params['term'] = self.term
        return params

    @property
    def summary(self):
        return f'{self.__class__.__name__} {self.term!r} in {self.database}'


def _serialize_ids(ids: Iterable[Identifier]) -> str:
    return ','.join([
        str(identifier) if isinstance(identifier, int) else identifier.strip()
        for identifier in ids
    ])


@dataclass
class SummaryQuery(EntrezQuery):
    """Functionality:
        - Returns document summaries (DocSums) for a list of input UIDs

    Parameters:
        database: Database from which to retrieve DocSums.
            Value must be a valid E-utility database name (default = :py:obj:`'pubmed'`).
        ids: UID list. Either a single UID or a comma-delimited list of UIDs may be provided.
            All of the UIDs must be from the database specified by :py:obj:`database`.
            There is no set maximum for the number of UIDs that can be passed to ESummary.
            To comply with the recommendation of using HTTP POST method if lists of UIDs for ESummary is long,
            the method is by default set to `post`.
        max_results: Maximal number of results to return. Limited to 10'000, following
            the eUtils documentation.
        ignore_max_results_limit: Ignore the upper limit placed on max_results.
            Experimentation has shown that some databases allow for higher limits, but
            as this is not documented, setting higher limits needs to be explicitly
            enabled here. Use at your own risk of hard to predict errors.
    """
    endpoint = 'esummary'
    method = 'post'
    ids: List[Identifier]
    max_results: int
    ignore_max_results_limit: bool = False

    def validate(self):
        super().validate()
        if self.max_results > 10_000 and not self.ignore_max_results_limit:
            raise ValueError('Fetching more than 10,000 results is not implemented')

    def to_params(self) -> Dict[str, str]:
        params = super().to_params()
        params['retmax'] = str(self.max_results)
        params['id'] = _serialize_ids(self.ids)
        return params

    @property
    def summary(self):
        ids_summary = self.ids if len(self.ids) <= 5 else f'{len(self.ids)} ids'
        return f'{self.__class__.__name__} {ids_summary} in {self.database}'


@dataclass
class FetchQuery(SummaryQuery):
    """
    Note: FetchQuery enforces xml as a default return_type as JSON is not properly implemented by the eutilis server.

    Functionality:
        - Returns formatted data records for a list of input UIDs

    Parameters:
        database: Database from which to retrieve records.
            Value must be a valid E-utility database name (default = :py:obj:`'pubmed'`).
            Currently EFetch does not support all Entrez databases.
            Please see `Table 1 <https://www.ncbi.nlm.nih.gov/books/n/helpeutils/chapter2/#chapter2.T._entrez_unique_identifiers_ui>`_ for a list of available databases.
        ids: UID list. Either a single UID or a comma-delimited list of UIDs may be provided.
            All of the UIDs must be from the database specified by :py:obj:`database`
        max_results: maximal number of results to return
    """
    # 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=11748933,11700088&retmode=xml'
    endpoint = 'efetch'
    return_type: ReturnType = 'xml'

    def to_params(self) -> Dict[str, str]:
        params = super().to_params()
        params['retmode'] = self.return_type
        return params


@dataclass
class LinkQuery(EntrezQuery):
    """
    Functionality:
        - Returns UIDs linked to an input set of UIDs in either the same or a different Entrez database
        - Returns UIDs linked to other UIDs in the same Entrez database that match an Entrez query
        - Checks for the existence of Entrez links for a set of UIDs within the same database
        - Lists the available links for a UID
        - Lists LinkOut URLs and attributes for a set of UIDs
        - Lists hyperlinks to primary LinkOut providers for a set of UIDs
        - Creates hyperlinks to the primary LinkOut provider for a single UID

    Parameters:
        database: Database to search. Value must be a valid E-utility database name (default = :py:obj:`'pubmed'`).
            This is the destination database for the link operation.
        database_from: Database to search. Value must be a valid E-utility database name (default = :py:obj:`'pubmed'`).
            This is the origin database of the link operation.
            If :py:obj:`database` and :py:obj:`database_from` are set to the same database value,
            then ELink will return computational neighbors within that database.
            Please see the full list of Entrez links for available computational neighbors.
            Computational neighbors have linknames that begin with dbname_dbname
            (examples: protein_protein, pcassay_pcassay_activityneighbor).
        ids: UID list. Either a single UID or a comma-delimited list of UIDs may be provided.
            All of the UIDs must be from the database specified by :py:obj:`database_from`
        command: ELink command mode. The command mode specifies which function ELink will perform.


    """
    # TODO: support cmd-specific parameters
    endpoint = 'elink'
    ids: List[Identifier]

    database_from: EntrezDatabase
    command: Command = 'neighbor'

    def to_params(self) -> Dict[str, str]:
        params = super().to_params()
        params['dbfrom'] = self.database_from
        params['id'] = _serialize_ids(self.ids)
        params['cmd'] = self.command
        return params


@dataclass
class CitationQuery(EntrezQuery):
    """
    Note: enforces xml as it is the only supported :py:obj:`return_type` for the citation endpoint.

    Functionality:
        - Retrieves PubMed IDs (PMIDs) that correspond to a set of input citations

    Parameters:
        database: Database to search. The only supported value is ‘pubmed’.
        citations: Input citations (dictionaries complying the with the :py:class:`~easy_entrez.types.Citation` interface).
    """
    endpoint = 'ecitmatch'

    database: Literal['pubmed']
    citations: List[Citation]
    return_type: ReturnType = 'xml'

    def to_params(self) -> Dict[str, str]:
        params = super().to_params()
        params['retmode'] = self.return_type
        params['bdata'] = '%0D'.join([
            '|'.join([
                citation['journal'].replace(' ', '+'),
                str(citation['year']),
                str(citation['volume']),
                str(citation['first_page']),
                citation['author'].replace(' ', '+'),
                citation['key'].replace(' ', '+')
            ]) + '|'
            for citation in self.citations
        ])
        return params


EXAMPLES: Dict[Type[EntrezQuery], List[Example]] = {
    LinkQuery: [
        Example(
            name='Link from protein to gene',
            query=LinkQuery(database_from='protein', database='gene', ids=[15718680, 157427902]),
            uri='elink.fcgi?db=gene&dbfrom=protein&id=15718680,157427902&cmd=neighbor'
        ),
        Example(
            name='Find articles related to PMID 20210808',
            query=LinkQuery(database='pubmed', database_from='pubmed', ids=[20210808], command='neighbor_score'),
            uri='elink.fcgi?db=pubmed&dbfrom=pubmed&id=20210808&cmd=neighbor_score'
        ),
        Example(
            name='List all possible links from two protein GIs',
            query=LinkQuery(database_from='protein', ids=[15718680, 157427902], command='acheck', database=None),
            uri='elink.fcgi?dbfrom=protein&id=15718680,157427902&cmd=acheck'
        ),
        Example(
            name='List all possible links from two protein GIs to PubMed',
            query=LinkQuery(database_from='protein', ids=[15718680, 157427902], command='acheck', database='pubmed'),
            uri='elink.fcgi?db=pubmed&dbfrom=protein&id=15718680,157427902&cmd=acheck'
        )
    ],
    CitationQuery: [
        Example(
            name='Check PMIDs for two citations',
            query=CitationQuery(
                database='pubmed',
                citations=[
                    dict(
                        journal='proc natl acad sci u s a',
                        year=1991,
                        volume=88,
                        first_page=3248,
                        author='mann bj',
                        key='Art1'
                    ),
                    Citation(
                        journal='science',
                        year=1987,
                        volume=235,
                        first_page=182,
                        author='palmenberg ac',
                        key='Art2'
                    )
                ]
            ),
            uri='ecitmatch.fcgi?db=pubmed&retmode=xml&bdata=proc+natl+acad+sci+u+s+a|1991|88|3248|mann+bj|Art1|%0Dscience|1987|235|182|palmenberg+ac|Art2|'
        )
    ],
    SearchQuery: [
        Example(
            name='Find articles about human cancers',
            query=SearchQuery(
                term='cancer AND human[organism]',
                database='pubmed',
                max_results=10000
            ),
            uri='esearch.fcgi?db=pubmed&retmax=10000&term=cancer AND human[organism]'
        ),
        Example(
            name='Search PubMed Central for free full text articles containing the query stem cells',
            query=SearchQuery(
                term='stem cells AND free fulltext[filter]',
                database='pmc',
                max_results=10000
            ),
            uri='esearch.fcgi?db=pmc&retmax=10000&term=stem cells AND free fulltext[filter]'
        )
    ]
}


def format_examples(examples, transformer=lambda x: x):
    return '\n    Examples:\n' + '\n'.join([
        f'        {example.name}\n\n        >>> {transformer(example.query)}\n'
        for example in examples
    ])


for query_, examples_ in EXAMPLES.items():
    query_.__raw_doc__ = query_.__doc__
    query_.__doc__ += format_examples(examples_)


def uses_query(query: Type[EntrezQuery]):

    def decorator(func):

        if not func.__doc__:
            func.__doc__ = ''

        if hasattr(query, '__raw_doc__'):
            func.__doc__ += query.__raw_doc__ + format_examples(
                EXAMPLES[query],
                transformer=lambda q: str(q).replace(query.__name__, 'entrez_api.' + func.__name__)
            )
        else:
            func.__doc__ += query.__doc__

        return func

    return decorator
