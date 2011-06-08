from setuptools import setup
setup(
    name = 'pytassium',
    version = '0.1.2',
    description = 'A Python library for working with Kasabi.com APIs',
    author='Ian Davis',
    author_email='nospam@iandavis.com',
    url='https://github.com/iand/pytassium',
    classifiers=['Programming Language :: Python','License :: Public Domain', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'Intended Audience :: Developers', 'Topic :: Software Development :: Libraries :: Python Modules', 'Topic :: Database'],
    packages =['pytassium'],
    install_requires=['rdfchangesets'],
    scripts = ["scripts/pytassium"],
    
)
