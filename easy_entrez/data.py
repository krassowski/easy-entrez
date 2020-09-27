from collections import defaultdict
from csv import DictReader
from pathlib import Path
from typing import Dict, List
from typing_extensions import TypedDict


class Table(TypedDict):
    """A table which is fast for both column and row access but quite memory-expensive"""
    columns: Dict[str, List]
    rows: Dict[str, List]


def _read_table(path: Path, index: str) -> Table:
    """Return dict where each entry is a data column"""
    table = {
        'columns': defaultdict(list),
        'rows': {}
    }
    with open(path) as f:
        reader = DictReader(f, delimiter='\t')
        for row in reader:
            for field, value in row.items():
                table['columns'][field].append(value)
            table['rows'][row[index]] = row
    return table


data_path = (Path(__file__).parent / 'data').resolve()
# https://www.ncbi.nlm.nih.gov/books/NBK25497/table/chapter2.T._entrez_unique_identifiers_ui/?report=objectonly
entrez_databases = _read_table(data_path / 'entrez_databases.tsv', index='E-utility Database Name')
entrez_database_codes = entrez_databases['columns']['E-utility Database Name']
