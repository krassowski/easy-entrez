from typing import Dict, Union, List, Literal
from xml.etree import ElementTree

# https://github.com/python/typing/issues/182
JSONType = Union[str, int, float, bool, None, Dict[str, 'JSON'], List['JSON']]
DataType = Union[JSONType, ElementTree.Element]


ReturnType = Literal['json', 'xml']

EntrezDatabaseType = Literal[
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


CommandType = Literal[
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
