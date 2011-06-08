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
import time
dataset = pytassium.Dataset('nasa','put-your-api-key-here')

# --------------------------
# Use the lookup API
# --------------------------
response, data = dataset.lookup('http://data.kasabi.com/dataset/nasa/person/eugeneandrewcernan')
if response.status in range(200,300):
  # data now contains an rdflib.Graph
  print data.serialize(format="turtle") 
else:
  print "Oh no! %d %s - %s" % (response.status, response.reason, body)

# --------------------------
# Use the sparql API
# --------------------------
response, data = dataset.select('select ?s where {?s a <http://xmlns.com/foaf/0.1/Person>} limit 10')
if response.status in range(200,300):
  # data now contains a dictionary of results
  print data
else:
  print "Oh no! %d %s - %s" % (response.status, response.reason, body)

# --------------------------
# Use the attribution API
# --------------------------
response, data = dataset.attribution()
# assuming success, data now contains dictionary
print data['homepage']

# --------------------------
# Use the search API
# --------------------------
# search for 5 results matching apollo
response, data = dataset.search("apollo", 5)
for result in data['results']:
  print "%s (score: %s)" % (result['title'], result['score'])

# facet on a search for alan, with the name and type fields
fields = ['name', 'type']
query = "alan"
response, data = dataset.facet(query, fields)
for facet in data['fields']:
  print "Top %ss matching %s" % (facet['name'],query)
  for term in facet['terms']:
    print "%s (%s results)" % (term['value'], term['number'])


# --------------------------
# Use the reconciliation API
# --------------------------
# Reconcile one label
response, data = dataset.reconcile('Alan Shepard')
print "Best match is: %s" % data['result'][0]['id']

# Reconcile a list of labels
labels = ['Neil Armstrong','alan shepard']
response, data = dataset.reconcile(labels)
for i in range(0, len(labels)):
  print "Best match for %s is: %s" % (labels[i], data['q%s'%i]['result'][0]['id'])

# Reconcile a label with specific parameters
response, data = dataset.reconcile('Apollo 11', limit=3, type='http://purl.org/net/schemas/space/Mission', type_strict ='any')
print "Best match is: %s" % data['result'][0]['id']

# Reconcile with a specific query
query = {
    "query" : "Apollo 11",
    "limit" : 3,
    "type" : "http://purl.org/net/schemas/space/Mission",
    "type_strict" : "any",
}
response, data = dataset.reconcile(query)
print "Best match is: %s" % data['result'][0]['id']

# --------------------------
# Use the update API
# --------------------------
dataset = pytassium.Dataset('my-writable-dataset','put-your-api-key-here')

# Store the contents of a turtle file
dataset.store_file('/tmp/mydata.ttl', media_type='text/turtle') 

# Store data from a string
mytriples = "<http://example.com/foo> a <http://example.com/Cat> ."
dataset.store_data(mytriples, media_type='text/turtle') 

# --------------------------
# Use the jobs API
# --------------------------
response, job_uri = dataset.schedule_reset()
print "Reset scheduled, URI is: %s" % job_uri
print "Waiting for reset to complete"
done = False
while not done:
  response, data = dataset.job_status(job_uri)
  if response.status in range(200,300):
    if data['status'] == 'scheduled':
      print "Reset has not started yet"
    elif data['status'] == 'running':
      print "Reset is in progress"
    elif data['status'] == 'failed':
      print "Reset has failed :("
      done = True
    elif data['status'] == 'succeeded':
      print "Reset has completed :)"
      done = True

  if not done:
    time.sleep(5)
```


Using pytassium command line
----------------------------
The pytassium package comes with a command line utility. Use it from the command line like this:
    
    pytassium
    
You'll be presented with a command prompt:

    >>>
    
First you need to tell it which dataset you want to work with. The "use" command does this. You can supply
the short name of the store or the full URI, it doesn't matter:

    >>> use nasa
    Using nasa

You also need to supply your API key:

    >>> apikey yourapikey

You can also specify the dataset and apikey using the -d and -a command line options:

    ./pytassium -d nasa -a yourapikey


To stop using pytassium use the "exit" command:

    >>> exit

### Exploring a dataset
pytassium has a number of commands that help with exploring a dataset. First up is "sample" which returns a sample of the subjects from the data:

    >>> sample
    0. http://data.kasabi.com/dataset/nasa/launchsite/russia
    1. http://data.kasabi.com/dataset/nasa/mission/apollo-10/role/lunar-module-pilot
    2. http://data.kasabi.com/dataset/nasa/person/eugeneandrewcernan
    3. http://data.kasabi.com/dataset/nasa/launchsite/tyuratambaikonurcosmodrome
    4. http://data.kasabi.com/dataset/nasa/launchsite/xichang
    5. http://data.kasabi.com/dataset/nasa/discipline/resupply/refurbishment/repair
    6. http://data.kasabi.com/dataset/nasa/mission/apollo-10
    7. http://www.bbc.co.uk/programmes/b00lg2xb#programme
    8. http://data.kasabi.com/dataset/nasa/mission/apollo-11
    9. http://data.kasabi.com/dataset/nasa/mission/apollo-11/role/backup-commander

You'll see that each URI is numbered. You can quickly describe that URI by typing the describe command followed by its number:

    >>> describe 1
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix space: <http://purl.org/net/schemas/space/> .

    <http://data.kasabi.com/dataset/nasa/mission/apollo-10/role/lunar-module-pilot> 
        a <http://purl.org/net/schemas/space/MissionRole>;
        rdfs:label "Apollo 10 Lunar Module Pilot";
        space:actor <http://data.kasabi.com/dataset/nasa/person/eugeneandrewcernan>;
        space:mission <http://data.kasabi.com/dataset/nasa/mission/apollo-10>;
        space:role <http://data.kasabi.com/dataset/nasa/roles/lunar-module-pilot> .

The numbers are remembered between each listing of URIs, so describe 2 will still work.

You can also describe by URI:

    >>> describe <http://www.bbc.co.uk/programmes/b00lg2xb#programme>
    @prefix dc: <http://purl.org/dc/elements/1.1/> .
    @prefix foaf: <http://xmlns.com/foaf/0.1/> .
    @prefix po: <http://purl.org/ontology/po/> .

    <http://www.bbc.co.uk/programmes/b00lg2xb#programme> a <http://purl.org/ontology/po/Episode>;
        dc:title "One Small Step";
        po:short_synopsis "The story of Neil Armstrong and Buzz Aldrin's trip to the moon.";
        foaf:primaryTopic <http://data.kasabi.com/dataset/nasa/mission/apollo-10>,
            <http://data.kasabi.com/dataset/nasa/mission/apollo-11>,
            <http://data.kasabi.com/dataset/nasa/person/edwineugenealdrinjr>,
            <http://data.kasabi.com/dataset/nasa/person/neilaldenarmstrong>;
        foaf:topic <http://data.kasabi.com/dataset/nasa/mission/apollo-10> .

You can get a count of the triples in a store:

    >>> count
    99448 triples

Or counts of various other types:

    >>> count subjects
    12357 subjects

    >>> count classes
    10 classes

    >>> count properties
    39 properties

You can also count occurrences of a class:

    >>> count <http://xmlns.com/foaf/0.1/Person>
    58 <http://xmlns.com/foaf/0.1/Person>

Or you can use the prefixed version (see below for more on prefixes)

    >>> count foaf:Person
    58 foaf:Person

The "show" command enables you to explore characteristics of the data:

    >>> show classes
    0. http://purl.org/net/schemas/space/MissionRole
    1. http://purl.org/net/schemas/space/Mission
    2. http://xmlns.com/foaf/0.1/Person
    3. http://purl.org/net/schemas/space/Spacecraft
    4. http://purl.org/net/schemas/space/Launch
    5. http://xmlns.com/foaf/0.1/Image
    6. http://purl.org/net/schemas/space/Discipline
    7. http://purl.org/net/schemas/space/LaunchSite
    8. http://purl.org/ontology/po/Episode
    9. http://rdfs.org/ns/void#Dataset

    >>> show properties
    0. http://purl.org/net/schemas/space/place
    1. http://www.w3.org/2000/01/rdf-schema#label
    2. http://www.w3.org/1999/02/22-rdf-syntax-ns#type
    3. http://purl.org/net/schemas/space/actor
    4. http://purl.org/net/schemas/space/role
    5. http://purl.org/net/schemas/space/mission
    6. http://xmlns.com/foaf/0.1/name
    7. http://purl.org/net/schemas/space/performed
    8. http://www.w3.org/2002/07/owl#sameAs
    9. http://purl.org/net/schemas/space/country
    10. http://xmlns.com/foaf/0.1/isPrimaryTopicOf
    11. http://purl.org/dc/elements/1.1/title
    12. http://purl.org/net/schemas/space/missionRole
    13. http://purl.org/ontology/po/short_synopsis

    >>> show topclasses
                        class                     | count
    ==============================================+======
    http://purl.org/net/schemas/space/Spacecraft  | 6692 
    http://purl.org/net/schemas/space/Launch      | 5090 
    http://xmlns.com/foaf/0.1/Image               | 303  
    http://purl.org/net/schemas/space/MissionRole | 142  
    http://xmlns.com/foaf/0.1/Person              | 58   


### Loading data
You can load data from a local file with the "store" command:

    >>> store yourdata.nt
    Uploading 'yourdata.nt'

The store command will automatically chunk ntriples files and load the pieces into the store. **Note: this does not take account of blank nodes so don't use store on files over 2MB if they contain blank nodes**

A future version will add support for the ingest service.

### Querying data
pytassium provides a "sparql" command to run a sparql query. It will attempt to format the results nicely.

    >>> sparql select * where {?s a <http://xmlns.com/foaf/0.1/Person>} limit 5
                                     s                                 
    ===================================================================
    http://data.kasabi.com/dataset/nasa/person/eugeneandrewcernan      
    http://data.kasabi.com/dataset/nasa/person/jamesarthurlovelljr     
    http://data.kasabi.com/dataset/nasa/person/richardfrancisgordonjr  
    http://data.kasabi.com/dataset/nasa/person/robertfranklynovermyer  
    http://data.kasabi.com/dataset/nasa/person/edgardeanmitchellusn/scd

The sparql command expands well known prefixes automatically:

    >>> sparql select ?title where {?s a space:Mission; dc:title ?title } limit 5
      title  
    =========
    Apollo 10
    Apollo 11
    Apollo 12
    Apollo 17
    Apollo 15

You can use "show prefixes" to list the recognised prefixes:

    >>> show prefixes
    foaf: <http://xmlns.com/foaf/0.1/>
    owl: <http://www.w3.org/2002/07/owl#>
    xsd: <http://www.w3.org/2001/XMLSchema#>
    bibo: <http://purl.org/ontology/bibo/>

You can add your own prefixes with the "prefix" command:

    >>> prefix ex <http://example.com/foo/>

By default, when pytassium starts up it attempts to fetch a list of common prefixes from http://prefix.cc. This file is cached
in the system temp directory for future use.

### Resetting a dataset
You can schedule a reset job on your dataset:

    >>> reset
    Scheduling reset job for immediate execution
    Reset scheduled, URI is: http://api.kasabi.com/dataset/id-test-dataset/jobs/8777c36e-a904-4498-b837-bcc214a9216d
    Reset has not started yet
    Reset is in progress
    Reset has completed

### Batch scripts
pytassium provides a -f command line options which specifies a filename containing commands to run. 
When pytassium is invoked with the -f option it reads the commands from the file, runs them and
then terminates

    ./pytassium -f /tmp/myscript
    
You can save the history from an interactive session with the "save" command:

    >>> save history /tmp/newscript
    
And execute the commands in any script with the "run" command:

    >>> run /tmp/newscript

### Command line operation
Any parameters supplied on the command line are assumed to a command for pytassium. It runs the command and then terminates:

    pytassium -a yourapikey -d nasa show classes
    0. http://purl.org/net/schemas/space/MissionRole
    1. http://purl.org/net/schemas/space/Mission
    2. http://xmlns.com/foaf/0.1/Person

Sparql queries will typically need to be enclosed in quotes:

    pytassium -a yourapikey -d nasa sparql "select * where {?s a <http://xmlns.com/foaf/0.1/Person>}"
                                     s                                 
    ===================================================================
    http://data.kasabi.com/dataset/nasa/person/eugeneandrewcernan      
    http://data.kasabi.com/dataset/nasa/person/jamesarthurlovelljr     
    http://data.kasabi.com/dataset/nasa/person/richardfrancisgordonjr  
    http://data.kasabi.com/dataset/nasa/person/robertfranklynovermyer  
    http://data.kasabi.com/dataset/nasa/person/edgardeanmitchellusn/scd

A common pattern is to reset a dataset and load some fresh data into it:

    pytassium -a yourapikey -d yourdataset reset
    pytassium -a yourapikey -d yourdataset store yourdata.nt

To-do
-----
The following APIs are not yet implemented:

* Augmentation

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
