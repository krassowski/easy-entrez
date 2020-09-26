# easy-entrez

Python REST API for Entrez E-Utilities, aiming to  be easy to use and reliable.

While other packages attempt to use stateful extensions (queries with history) which is error-prone and led to misleading results, this implementation:
 - avoids the problem altogether by not using such stateful API,
 - makes common tasks easy thanks to Pythonic API,
 - is typed and integrates well with mypy

**Stats:** Beta

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

See more in the [Demo notebook](./Demo.ipynb).


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

- [biopython.Entrez](https://biopython.org/docs/1.74/api/Bio.Entrez.html)
- entrezpy
