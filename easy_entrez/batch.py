from functools import wraps
from math import ceil
from time import sleep
from typing import Sequence
from warnings import warn

from requests import RequestException

class TqdmMock:
    total: int
    def update(self, i: int):
        pass


try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable=None):
        if iterable is None:
            return TqdmMock()
        return iterable


def batches(data, size=100):
    return [
        data[i * size:(i + 1) * size]
        for i in range(0, ceil(len(data) / size))
    ]


def supports_batches(func):
    """
    Call the decorated functions with the collection from the first argument
    (second if counting with self) split into batches, resuming on failures
    with a interval twice the between-batch interval.
    """

    @wraps(func)
    def batches_support_wrapper(self: 'EntrezAPI', collection: Sequence, *args, **kwargs):
        size = self._batch_size
        interval = self._batch_sleep_interval
        if size is not None:
            assert isinstance(size, int)
            by_batch = {}

            for i, batch in enumerate(tqdm(batches(collection, size=size))):
                done = False

                while not done:
                    reason = None
                    try:
                        batch_result = func(self, batch, *args, **kwargs)
                        code = batch_result.response.status_code
                        if code == 200:
                            done = True
                        else:
                            reason = f'Status code != 200 (= {code})'
                    except RequestException as e:
                        reason = e

                    if not done:
                        warn(
                            f'Failed to fetch for {i}-th batch, retrying in {interval * 2} seconds.'
                            f' The reason was: {reason}'
                        )
                        sleep(interval * 2)

                by_batch[tuple(batch)] = batch_result
                sleep(interval)
            return by_batch
        else:
            return func(self, collection, *args, **kwargs)

    if not batches_support_wrapper.__doc__:
        batches_support_wrapper.__doc__ = ''

    batches_support_wrapper.__doc__ += '\n    Supports batch mode, see :py:meth:`~EntrezAPI.in_batches_of`.'

    return batches_support_wrapper


def supports_pagination(func):
    """
    Call the decorated functions with the collection from the first argument
    (second if counting with self) split into pages, resuming on failures
    with a interval twice the between-page interval.
    """

    @wraps(func)
    def pagination_support_wrapper(self: 'EntrezAPI', *args, **kwargs):
        size = self._page_size
        interval = self._page_sleep_interval
        if size is not None:
            assert isinstance(size, int)
            by_page = {}
            page = 0
            count = None
            downloaded = 0
            progress = tqdm()
            if 'max_results' in kwargs:
               del kwargs['max_results']

            finished = False
            while not finished:
                done = False

                while not done:
                    reason = None
                    try:
                        page_result = func(self, *args, **kwargs, resume_from=page * size, max_results=size)
                        code = page_result.response.status_code
                        result_type = page_result.data['header']['type']
                        result_info = page_result.data[f'{result_type}result']
                        count = int(result_info['count'])
                        progress.total = count
                        downloaded += size
                        page += 1
                        progress.update(downloaded)
                        assert page * size == int(result_info['retstart'])
                        assert size == int(result_info['retmax'])
                        if code == 200:
                            done = True
                        else:
                            reason = f'Status code != 200 (= {code})'
                    except RequestException as e:
                        reason = e

                    if not done:
                        warn(
                            f'Failed to fetch for {page}-th page, retrying in {interval * 2} seconds.'
                            f' The reason was: {reason}'
                        )
                        sleep(interval * 2)

                if count is None:
                    raise ValueError('Count not set after first page')
                if downloaded >= count:
                    finished = True
                by_page[page] = page_result
                sleep(interval)
            return by_page
        else:
            return func(self, collection, *args, **kwargs)

    if not pagination_support_wrapper.__doc__:
        pagination_support_wrapper.__doc__ = ''

    pagination_support_wrapper.__doc__ += '\n    Supports pagination mode, see :py:meth:`~EntrezAPI.page_by_page`.'

    return pagination_support_wrapper
