from warnings import warn
from typing import Dict, List
from dataclasses import dataclass

from pandas import read_table

from .types import ReturnType, EntrezDatabaseType, CommandType

from pathlib import Path


# https://www.ncbi.nlm.nih.gov/books/NBK25497/table/chapter2.T._entrez_unique_identifiers_ui/?report=objectonly
data_path = (Path(__file__).parent / 'data').resolve()
entrez_databases = read_table(data_path / 'entrez_databases.tsv')

entrez_database_codes = entrez_databases['E-utility Database Name'].tolist()


@dataclass
class EntrezQuery:

    database: EntrezDatabaseType
    method = 'get'
    endpoint_suffix = '.fcgi'

    def validate(self):
        if self.database not in entrez_database_codes:
            warn(f'Unknown database: {self.database}')

    @property
    def uid_meaning(self):
        return entrez_databases.set_index('E-utility Database Name')

    def to_params(self) -> Dict[str, str]:
        """Convert to params which can be accepted by Entrez"""
        # TODO maybe use pydantic isntead?
        self.validate()
        params = {}
        if self.database:
            params['db'] = self.database
        return params

    @property
    def summary(self):
        return f'{self.__class__.__name__} in {self.database}'


@dataclass
class InfoQuery(EntrezQuery):
    endpoint = 'einfo'


@dataclass
class SearchQuery(EntrezQuery):
    """
    Functions:
        - Provides a list of UIDs matching a text query
        - Posts the results of a search on the History server
        - Downloads all UIDs from a dataset stored on the History server
        - Combines or limits UID datasets stored on the History server
        - Sorts sets of UIDs

    Required Parameters:
        database: Database to search. Value must be a valid E-utility database name - see `entrez_database_codes` (default = `'pubmed'`).
        term: Entrez text query

    """
    endpoint = 'esearch'
    term: str
    max_results: int

    def validate(self):
        super().validate()
        if self.max_results > 100_000:
            raise ValueError('Fetching more than 100,000 results is not implemented')

    def to_params(self) -> Dict[str, str]:
        params = super().to_params()
        params['retmax'] = str(self.max_results)
        params['term'] = self.term
        return params

    @property
    def summary(self):
        return f'{self.__class__.__name__} {self.term!r} in {self.database}'


@dataclass
class SummaryQuery(EntrezQuery):
    """
    Functions:
        - Returns document summaries (DocSums) for a list of input UIDs
        - Returns DocSums for a set of UIDs stored on the Entrez History server

    Required Parameters:
        database: Database to search. Value must be a valid E-utility database name - see `entrez_database_codes` (default = `'pubmed'`).
        ids: UID list. Either a single UID or a comma-delimited list of UIDs may be provided. All of the UIDs must be from the database specified by `database`
    """
    endpoint = 'esummary'
    method = 'post'
    ids: List[str]
    max_results: int

    def validate(self):
        super().validate()
        if self.max_results > 10_000:
            raise ValueError('Fetching more than 10,000 results is not implemented')

    def to_params(self) -> Dict[str, str]:
        params = super().to_params()
        params['retmax'] = str(self.max_results)
        params['id'] = ','.join([
            id.strip()
            for id in self.ids
        ])
        return params

    @property
    def summary(self):
        ids_summary = self.ids if len(self.ids) <= 5 else f'{len(self.ids)} ids'
        return f'{self.__class__.__name__} {ids_summary} in {self.database}'


@dataclass
class FetchQuery(SummaryQuery):
    """
    It enforces xml as a default return_type as JSON is not properly implemented by the eutilis server yet.
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
    Functions:
        Returns UIDs linked to an input set of UIDs in either the same or a different Entrez database
        Returns UIDs linked to other UIDs in the same Entrez database that match an Entrez query
        Checks for the existence of Entrez links for a set of UIDs within the same database
        Lists the available links for a UID
        Lists LinkOut URLs and attributes for a set of UIDs
        Lists hyperlinks to primary LinkOut providers for a set of UIDs
        Creates hyperlinks to the primary LinkOut provider for a single UID

    """
    endpoint = 'elink'

    database_from: EntrezDatabaseType
    command: CommandType = 'neighbor'
