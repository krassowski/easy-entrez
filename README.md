# easy-entrez

**Goal:** Create Python REST API for Entrez E-Utilities, which will be easy to use and reliable, but limited in scope (no stateful/history queries).

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


Alternatives:
  - [biopython.Entrez](https://biopython.org/docs/1.74/api/Bio.Entrez.html)
  - entrezpy
