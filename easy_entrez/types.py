from dataclasses import dataclass
from typing import Dict, Union, List, TypeVar, Any
from typing_extensions import TypedDict, Literal
try:
    from typing import get_args
except ImportError:

    def get_args(annotation):
        try:
            return annotation.__args__
        except AttributeError:
            # Python 3.6
            return []


from xml.etree import ElementTree

from .data import entrez_databases


# support minimal typing up to third level of nesting
# (recursive typing not yet supported, see: https://github.com/python/typing/issues/182)
JSONType0 = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
JSONType1 = Union[str, int, float, bool, None, Dict[str, JSONType0], List[JSONType0]]
JSONType = Union[str, int, float, bool, None, Dict[str, JSONType1], List[JSONType1]]

ReturnType = Literal['json', 'xml']
DataType = TypeVar('DataType', bound=Union[JSONType, ElementTree.Element])


_EntrezDatabaseType = Literal[
    'bioproject',
    'biosample',
    'biosystems',
    'books',
    'cdd',
    'gap',
    'dbvar',
    'epigenomics',
    'nucest',
    'gene',
    'genome',
    'gds',
    'geoprofiles',
    'nucgss',
    'homologene',
    'mesh',
    'toolkit',
    'ncbisearch',
    'nlmcatalog',
    'nuccore',
    'omia',
    'popset',
    'probe',
    'protein',
    'proteinclusters',
    'pcassay',
    'pccompound',
    'pcsubstance',
    'pubmed',
    'pmc',
    'snp',
    'sra',
    'structure',
    'taxonomy',
    'unigene',
    'unists'
]


def list_literal_values(type_annotation, modifier: lambda x: x):
    return '\n' + '\n'.join(
        [f'- {modifier(arg)}' for arg in get_args(type_annotation)]
    )


class EntrezDatabaseType:
    """The database to be used, one of:
    """


EntrezDatabase = EntrezDatabaseType()
EntrezDatabase.__supertype__ = _EntrezDatabaseType
EntrezDatabaseType.__doc__ += list_literal_values(
    _EntrezDatabaseType,
    modifier=lambda arg: f':py:obj:`\'{arg}\'` - {entrez_databases["rows"][arg]["Entrez Database"]}'
)

_CommandType = Literal[
    'neighbor',
    'neighbor_score',
    'neighbor_history',
    'acheck',
    'ncheck',
    'lcheck',
    'llinks',
    'llinkslib',
    'prlinks'
]

command_descriptions = {
    'neighbor': 'return a set of UIDs in *database* linked to the input UIDs in *database_from*.',
    'neighbor_score': 'return a set of UIDs within the same database as the input UIDs along with computed similarity scores.',
    'neighbor_history': 'post the output UIDs to the Entrez History server and returns a query_key and WebEnv corresponding to the location of the output set.',
    'acheck': 'list all links available for a set of UIDs.',
    'ncheck': 'check for the existence of links within the same database for a set of UIDs. These links are equivalent to setting *database* and *database_from* to the same value.',
    'lcheck': 'check for the existence of external links (LinkOuts) for a set of UIDs.',
    'llinks': 'for each input UID, list the URLs and attributes for the LinkOut providers that are not libraries.',
    'llinkslib': 'for each input UID, list the URLs and attributes for *all* LinkOut providers including libraries.',
    'prlinks': 'list the primary LinkOut provider for each input UID, or links directly to the LinkOut provider\'s web site for a single UID if *return_mode* is set to *ref*.'
}


class CommandType:
    """The command for the ELnk query, one of:
    """


Command = CommandType()
Command.__supertype__ = _CommandType
CommandType.__doc__ += list_literal_values(
    _CommandType,
    modifier=lambda arg: f':py:obj:`\'{arg}\'`\n\t{command_descriptions[arg]}\n'
)


_IdentifierType = Union[str, int]

Identifier = _IdentifierType


@dataclass
class Example:
    name: str
    query: 'EntrezQuery'
    uri: str


class Citation(TypedDict):
    """Dictionary with the citation input data having the following keys and values:"""
    #: Journal title, e.g. ‘science‘ or ‘proc natl acad sci u s a‘
    journal: str
    #: Year
    year: int
    #: Volume
    volume: int
    #: First page
    first_page: int
    #: Author name, e.g. ‘mann bj‘ or ‘palmenberg ac‘
    author: str
    #: Identifier that will help you recognise the citation in the results, e.g. ‘Art1‘ or ‘Art2‘
    key: str
