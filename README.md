# easy-entrez

![tests](https://github.com/krassowski/easy-entrez/workflows/tests/badge.svg)
![CodeQL](https://github.com/krassowski/easy-entrez/workflows/CodeQL/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/easy-entrez/badge/?version=latest)](https://easy-entrez.readthedocs.io/en/latest/?badge=latest)

Python REST API for Entrez E-Utilities, aiming to  be easy to use and reliable.

Easy-entrez:

- makes common tasks easy thanks to simple Pythonic API,
- is typed and integrates well with mypy,
- is tested on Windows, Mac and Linux across Python 3.7, 3.8, 3.9 and 3.10,
- is limited in scope, allowing to focus on the reliability of the core code,
- does not use the stateful API as it is [error-prone](https://gitlab.com/ncbipy/entrezpy/-/issues/7) as seen on example of the alternative *entrezpy*.


**Status:** beta (pending tutorial write-up and documentation improvements before official release).

```python
from easy_entrez import EntrezAPI

entrez_api = EntrezAPI(
    'your-tool-name',
    'e@mail.com',
    # optional
    return_type='json'
)

# find up to 10 000 results for cancer in human
result = entrez_api.search('cancer AND human[organism]', max_results=10_000)

# data will be populated with JSON or XML (depending on the `return_type` value)
result.data
```

See more in the [Demo notebook](./Demo.ipynb) and [documentation](https://easy-entrez.readthedocs.io/en/latest).

For a real-world example (i.e. used for [this publication](https://www.frontiersin.org/articles/10.3389/fgene.2020.610798/full)) see notebooks in [multi-omics-state-of-the-field](https://github.com/krassowski/multi-omics-state-of-the-field) repository.

#### Example: fetching genes for a variant from dbSNP 

Fetch the SNP record for `rs6311`:

```python
rs6311 = entrez_api.fetch(['rs6311'], max_results=1, database='snp').data[0]
rs6311
```

Display the result:

```python
from easy_entrez.parsing import xml_to_string

print(xml_to_string(rs6311))
```

Find the gene names for `rs6311`:

```python
namespaces = {'ns0': 'https://www.ncbi.nlm.nih.gov/SNP/docsum'}
genes = [
    name.text
    for name in rs6311.findall('.//ns0:GENE_E/ns0:NAME', namespaces)
]
print(genes)
```

> `['HTR2A']`

Fetch data for multiple variants at once:

```python
result = entrez_api.fetch(['rs6311', 'rs662138'], max_results=10, database='snp')
gene_names = {
    'rs' + document_summary.get('uid'): [
        element.text
        for element in document_summary.findall('.//ns0:GENE_E/ns0:NAME', namespaces)
    ]
    for document_summary in result.data
}
print(gene_names)
```

> `{'rs6311': ['HTR2A'], 'rs662138': ['SLC22A1']}`

#### Example: obtaining the chromosomal position from SNP rsID number

```python
from pandas import DataFrame

result = entrez_api.fetch(['rs6311', 'rs662138'], max_results=10, database='snp')

variant_positions = DataFrame([
    {
        'id': 'rs' + document_summary.get('uid'),
        'chromosome': chromosome,
        'position': position
    }
    for document_summary in result.data
    for chrom_and_position in document_summary.findall('.//ns0:CHRPOS', namespaces)
    for chromosome, position in [chrom_and_position.text.split(':')]
])

variant_positions
```

> |    | id       |   chromosome |   position |
> |---:|:---------|-------------:|-----------:|
> |  0 | rs6311   |           13 |   46897343 |
> |  1 | rs662138 |            6 |  160143444 |


#### Example: obtaining the SNP rs ID number from chromosomal position

You can use the query string directly:

```python
results = entrez_api.search(
    '13[CHROMOSOME] AND human[ORGANISM] AND 31873085[POSITION]',
    database='snp',
    max_results=10
)
print(results.data['esearchresult']['idlist'])
```

> `['59296319', '17076752', '7336701', '4']`

Or pass a dictionary (no validation of arguments is performed, `AND` conjunction is used):

```python
results = entrez_api.search(
    dict(chromosome=13, organism='human', position=31873085),
    database='snp',
    max_results=10
)
print(results.data['esearchresult']['idlist'])
```

> `['59296319', '17076752', '7336701', '4']`

The base position should use the latest genome assembly (GRCh38 at the time of writing);
you can use the position in previous assembly coordinates by replacing `POSITION` with `POSITION_GRCH37`.
For more information of the arguments accepted by the SNP database see the [entrez help page](https://www.ncbi.nlm.nih.gov/snp/docs/entrez_help/) on NCBI website.

### Installation

Requires Python 3.6+. Install with:


```bash
pip install easy-entrez
```

If you wish to enable (optional, tqdm-based) progress bars use:

```bash
pip install easy-entrez[with_progress_bars]
```

### Alternatives:

You might want to try:

- [biopython.Entrez](https://biopython.org/docs/1.74/api/Bio.Entrez.html) - biopython is a heavy dependency, but probably good choice if you already use it
- [pubmedpy](https://github.com/dhimmel/pubmedpy) - provides interesting utilities for parsing the responses
- [entrez](https://github.com/jordibc/entrez) - appears to have a comparable scope but quite different API

I have tried and do not recommend:

- [entrezpy](https://gitlab.com/ncbipy/entrezpy) - in addition to the history problems, watch out for [documentation issues](https://gitlab.com/ncbipy/entrezpy/-/issues/8) and basically [no reaction](https://gitlab.com/ncbipy/entrezpy/-/merge_requests/1) to pull requests.
