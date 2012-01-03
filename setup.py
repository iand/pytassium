from setuptools import setup
import os, re
name = 'pytassium'
version_number_re = "\s*__version__\s*=\s*((\"([^\"]|\\\\\")*\"|'([^']|\\\\')*'))"
version_file = os.path.join(os.path.dirname(__file__), name, '__init__.py')
version_number = re.search(version_number_re, open(version_file).read()).groups()[0][1:-1]

setup(
    name = name,
    version = version_number,
    description = 'A Python library for working with Kasabi.com APIs',
    author='Ian Davis',
    author_email='nospam@iandavis.com',
    url='https://github.com/iand/pytassium',
    classifiers=['Programming Language :: Python','License :: Public Domain', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'Intended Audience :: Developers', 'Topic :: Software Development :: Libraries :: Python Modules', 'Topic :: Database'],
    packages =['pytassium'],
    install_requires=['rdfchangesets', 'TurtleLexer', 'httplib2', 'rdflib>=3.1.0'],
    scripts = ["scripts/pytassium"],
    
)
