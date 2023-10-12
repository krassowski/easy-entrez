from setuptools import setup
from setuptools import find_packages


def get_long_description(file_name):
    with open(file_name) as f:
        return f.read()


if __name__ == '__main__':
    setup(
        name='easy_entrez',
        packages=find_packages(),
        package_data={'easy_entrez': ['data/*.tsv', 'py.typed']},
        # required for mypy to work
        zip_safe=False,
        version='0.3.7',
        license='MIT',
        description='Python REST API for Entrez E-Utilities: stateless, easy to use, reliable.',
        long_description=get_long_description('README.md'),
        long_description_content_type='text/markdown',
        author='Michal Krassowski',
        author_email='krassowski.michal+pypi@gmail.com',
        url='https://github.com/krassowski/easy-entrez',
        keywords=['entrez', 'pubmed', 'e-utilities', 'ncbi', 'rest', 'api', 'dbsnp', 'literature', 'mining'],
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX :: Linux',
            'Operating System :: MacOS',
            'Topic :: Utilities',
            'Topic :: Database',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Typing :: Typed',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11'
        ],
        install_requires=['requests', 'typing_extensions'],
        extras_require={
            'with_progress_bars': ['tqdm'],
            'with_parsing_utils': ['pandas'],
            'docs': [
                'sphinx<6.0',
                'pydata-sphinx-theme',
                'sphinx-autodoc-typehints',
                'sphinx-copybutton',
                'myst-parser'
            ]
        }
    )
