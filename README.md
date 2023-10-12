# easy-entrez

![tests](https://github.com/krassowski/easy-entrez/workflows/tests/badge.svg)
![CodeQL](https://github.com/krassowski/easy-entrez/workflows/CodeQL/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/easy-entrez/badge/?version=latest)](https://easy-entrez.readthedocs.io/en/latest/?badge=latest)
[![DOI](https://zenodo.org/badge/272182307.svg)](https://zenodo.org/badge/latestdoi/272182307)

Python REST API for Entrez E-Utilities, aiming to  be easy to use and reliable.

Easy-entrez:

- makes common tasks easy thanks to simple Pythonic API,
- is typed and integrates well with mypy,
- is tested on Windows, Mac and Linux across Python 3.7, 3.8, 3.9, 3.10 and 3.11
- is limited in scope, allowing to focus on the reliability of the core code,
- does not use the stateful API as it is [error-prone](https://gitlab.com/ncbipy/entrezpy/-/issues/7) as seen on example of the alternative *entrezpy*.


### Examples

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

#### Fetching genes for a variant from dbSNP

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

#### Obtaining the chromosomal position from SNP rsID number

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


#### Converting full variation/mutation data to tabular format

Parsing utilities can quickly extract the data to a `VariantSet` object
holding pandas `DataFrame`s with coordinates and alternative alleles frequencies:

```python
from easy_entrez.parsing import parse_dbsnp_variants

variants = parse_dbsnp_variants(result)
variants
```

> `<VariantSet with 2 variants>`

To get the coordinates:

```python
variants.coordinates
```

> | rs_id    | ref   | alts   |   chrom |       pos |   chrom_prev |   pos_prev | consequence                                                                  |
> |:---------|:------|:-------|--------:|----------:|-------------:|-----------:|:-----------------------------------------------------------------------------|
>| rs6311   | C     | A,T    |      13 |  46897343 |           13 |   47471478 | upstream_transcript_variant,intron_variant,genic_upstream_transcript_variant |
>| rs662138 | C     | G      |       6 | 160143444 |            6 |  160564476 | intron_variant                                                               |

For frequencies:

```python
variants.alt_frequencies.head(5)  # using head to only display first 5 for brevity
```

> |    | rs_id   | allele   |   source_frequency |   total_count | study       |     count |
> |---:|:--------|:---------|-------------------:|--------------:|:------------|----------:|
> |  0 | rs6311  | T        |           0.44349  |          2221 | 1000Genomes |   984.991 |
> |  1 | rs6311  | T        |           0.411261 |          1585 | ALSPAC      |   651.849 |
> |  2 | rs6311  | T        |           0.331696 |          1486 | Estonian    |   492.9   |
> |  3 | rs6311  | T        |           0.35     |            14 | GENOME_DK   |     4.9   |
> |  4 | rs6311  | T        |           0.402529 |         56309 | GnomAD      | 22666     |


#### Obtaining the SNP rs ID number from chromosomal position

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

#### Obtaining amino acids change information for variants in given range

First we search for dbSNP rs identifiers for variants in given region:

```python
dbsnp_ids = (
    entrez_api
    .search(
        '12[CHROMOSOME] AND human[ORGANISM] AND 21178600:21178720[POSITION]',
        database='snp',
        max_results=100
    )
    .data
    ['esearchresult']
    ['idlist']
)
```

Then fetch the variant data for identifiers:

```python
variant_data = entrez_api.fetch(
    ['rs' + rs_id for rs_id in dbsnp_ids],
    max_results=10,
    database='snp'
)
```

And parse the data, extracting the HGVS out of summary:

```python
from easy_entrez.parsing import parse_dbsnp_variants
from pandas import Series


def select_protein_hgvs(items):
    return [
        [sequence, hgvs]
        for entry in items
        for sequence, hgvs in [entry.split(':')]
        if hgvs.startswith('p.')
    ]


protein_hgvs = (
    parse_dbsnp_variants(variant_data)
    .summary
    .HGVS
    .apply(select_protein_hgvs)
    .explode()
    .dropna()
    .apply(Series)
    .rename(columns={0: 'sequence', 1: 'hgvs'})
)
protein_hgvs.head()
```

> | rs_id        | sequence    | hgvs        |
> |:-------------|:------------|:------------|
> | rs1940853486 | NP_006437.3 | p.Gly203Ter |
> | rs1940853414 | NP_006437.3 | p.Glu202Gly |
> | rs1940853378 | NP_006437.3 | p.Glu202Lys |
> | rs1940853299 | NP_006437.3 | p.Lys201Thr |
> | rs1940852987 | NP_006437.3 | p.Asp198Glu |

#### Fetching more than 10 000 entries

Use `in_batches_of` method to fetch more than 10k entries (e.g. `variant_ids`):

```python
snps_result = (
    entrez.api
    .in_batches_of(1_000)
    .fetch(variant_ids, max_results=5_000, database='snp')
)
```

The result is a dictionary with keys being identifiers used in each batch (because the Entrez API does not always return the indentifiers back) and values representing the result. You can use `parse_dbsnp_variants` directly on this dictionary.

#### Find PubMed ID from DOI

When searching GWAS catalog PMID is needed over DOI. You can covert one to the other using:

```python
def doi_term(doi: str) -> str:
    """Prepare DOI for PubMed search"""
    doi = (
        doi
        .replace('http://', 'https://')
        .replace('https://doi.org/', '')
    )
    return f'"{doi}"[Publisher ID]'


result = entrez_api.search(
    doi_term('https://doi.org/10.3389/fcell.2021.626821'),
    database='pubmed',
    max_results=1
)
result.data['esearchresult']['idlist']
```

> `['33834021']`

### Installation

Requires Python 3.6+. Install with:


```bash
pip install easy-entrez
```

If you wish to enable (optional, tqdm-based) progress bars use:

```bash
pip install easy-entrez[with_progress_bars]
```

If you wish to enable (optional, pandas-based) parsing utilities use:

```bash
pip install easy-entrez[with_parsing_utils]
```

### Alternatives

You might want to try:

- [biopython.Entrez](https://biopython.org/docs/1.74/api/Bio.Entrez.html) - biopython is a heavy dependency, but probably good choice if you already use it
- [pubmedpy](https://github.com/dhimmel/pubmedpy) - provides interesting utilities for parsing the responses
- [entrez](https://github.com/jordibc/entrez) - appears to have a comparable scope but quite different API
- [entrezpy](https://gitlab.com/ncbipy/entrezpy) - this one did not work well for me (hence this package), but may have improved since
