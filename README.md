# easy-entrez

![tests](https://github.com/krassowski/easy-entrez/workflows/tests/badge.svg)
![CodeQL](https://github.com/krassowski/easy-entrez/workflows/CodeQL/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/easy-entrez/badge/?version=latest)](https://easy-entrez.readthedocs.io/en/latest/?badge=latest)

Python REST API for Entrez E-Utilities, aiming to  be easy to use and reliable.

Easy-entrez:

- makes common tasks easy thanks to simple Pythonic API,
- is typed and integrates well with mypy,
- is tested on Windows, Mac and Linux across Python 3.6, 3.7, and 3.8,
- is limited in scope, allowing to focus on the reliability of the core code,
- does not use the stateful API as it is [error-prone](https://gitlab.com/ncbipy/entrezpy/-/issues/7) as seen on example of the alternative *entrezpy*.


**Stats:** beta (pending tutorial write-up and documentation improvements before official release).

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
