from setuptools import setup
from setuptools import find_packages


try:
    from pypandoc import convert

    def get_long_description(file_name):
        return convert(file_name, 'rst', 'md')

except ImportError:

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
        version='0.1.4',
        license='MIT',
        description='Python REST API for Entrez E-Utilities: stateless, easy to use, reliable.',
        long_description=get_long_description('README.md'),
        author='Michal Krassowski',
        author_email='krassowski.michal+pypi@gmail.com',
        url='https://github.com/krassowski/easy-entrez',
        keywords=['entrez', 'pubmed', 'e-utilities', 'ncbi', 'rest', 'api'],
        classifiers=[
            'Development Status :: 4 - Beta',
            'License :: OSI Approved :: MIT License',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX :: Linux',
            'Topic :: Utilities',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8'
        ],
        install_requires=['requests'],
        extras_require={
            'with_progress_bars': ['tqdm']
        }
    )
