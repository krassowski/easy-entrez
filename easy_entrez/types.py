from dataclasses import dataclass
from typing import Dict, Union, List
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
JSONType0 = Union[str, int, float, bool, None, Dict[str, any], List[any]]
JSONType1 = Union[str, int, float, bool, None, Dict[str, JSONType0], List[JSONType0]]
JSONType = Union[str, int, float, bool, None, Dict[str, JSONType1], List[JSONType1]]
DataType = Union[JSONType, ElementTree.Element]


ReturnType = Literal['json', 'xml']

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
        [f'\t- {modifier(arg)}' for arg in get_args(type_annotation)]
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


class CommandType:
    """The command for the ELnk query, one of:
    """


Command = CommandType()
Command.__supertype__ = _CommandType
CommandType.__doc__ += list_literal_values(
    _CommandType,
    modifier=lambda arg: f':py:obj:`\'{arg}\'`'
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
