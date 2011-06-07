pytassium
=========
A Python library for working with Kasabi.com APIs.

Overview
--------
This is a library for working with APIs provided by [Kasabi](http://www.kasabi.com/)

Homepage: http://github.com/iand/pytassium
Pypi: http://pypi.python.org/pypi/pytassium

Installing
----------
Install with easy_install:

    >sudo easy_install pytassium

If you already have it installed then simply upgrade with:

    >sudo easy_install --upgrade pytassium

pytassium requires the following (should be handled automatically with easy_install):

*   [rdfchangesets](https://github.com/iand/rdfchangesets)

Getting Started
---------------
The basic pattern of usage is as follows:

```python
import pytassium
dataset = pytassium.Dataset('nasa','put-your-api-key-here')

# Use the lookup API
response, data = dataset.lookup('http://data.kasabi.com/dataset/nasa/person/eugeneandrewcernan')
if response.status in range(200,300):
  # data now contains an rdflib.Graph
  print data.serialize(format="turtle") 
else:
  print "Oh no! %d %s - %s" % (response.status, response.reason, body)

# Use the sparql API
response, data = dataset.select('select ?s where {?s a <http://xmlns.com/foaf/0.1/Person>} limit 10')
if response.status in range(200,300):
  # data now contains a dictionary of results
  print data
else:
  print "Oh no! %d %s - %s" % (response.status, response.reason, body)

# Use the attribution API
response, data = dataset.attribution()
# assuming success, data now contains dictionary
print data['homepage']

# Use the reconciliation API

# Reconcile one label
response, data = d.reconcile('Alan Shepard')
print "Best match is: %s" % data['result'][0]['id']

# Reconcile a list of labels
labels = ['Neil Armstrong','alan shepard']
response, data = d.reconcile(labels)
for i in range(0, len(labels)):
  print "Best match for %s is: %s" % (labels[i], data['q%s'%i]['result'][0]['id'])


# Reconcile a label with specific parameters
response, data = d.reconcile('Apollo 11', limit=3, type='http://purl.org/net/schemas/space/Mission', type_strict ='any')
print "Best match is: %s" % data['result'][0]['id']

# Reconcile with a specific query
query = {
    "query" : "Apollo 11",
    "limit" : 3,
    "type" : "http://purl.org/net/schemas/space/Mission",
    "type_strict" : "any",
}
response, data = d.reconcile(query)
print "Best match is: %s" % data['result'][0]['id']

# Use the update API
dataset = pytassium.Dataset('my-writable-dataset','put-your-api-key-here')

# Store the contents of a turtle file
dataset.store_file('/tmp/mydata.ttl', media_type='text/turtle') 

# Store data from a string
mytriples = "<http://example.com/foo> a <http://example.com/Cat> ."
dataset.store_data(mytriples, media_type='text/turtle') 
```

To-do
-----
The following APIs are not yet implemented:

* Search
* Augmentation
* Reconciliation
* Jobs

Related Projects
----------------
If Python's not your thing, you may also be interested in:

* [kasabi.rb](https://github.com/kasabi/kasabi.rb) - Ruby
* [potassium](https://github.com/iand/potassium) - PHP

Author
------
[Ian Davis](http://iandavis.com/), nospam@iandavis.com

Licence
-------
This work is hereby released into the Public Domain. 

To view a copy of the public domain dedication, visit 
[http://creativecommons.org/licenses/publicdomain](http://creativecommons.org/licenses/publicdomain) or send a letter to 
Creative Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
