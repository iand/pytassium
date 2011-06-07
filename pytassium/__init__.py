# pytassium
# This work is hereby released into the Public Domain. 
#
# To view a copy of the public domain dedication, visit 
# [http://creativecommons.org/licenses/publicdomain](http://creativecommons.org/licenses/publicdomain) 
# or send a letter to Creative Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.


__all__ = ["Dataset", "PytassiumError"]

import httplib2
#httplib2.debuglevel=1
import urllib
from rdflib.graph import Graph
from rdflib.namespace import Namespace
from rdflib.term import URIRef, Literal, BNode
from rdflib.parser import StringInputSource
import datetime as dt
import StringIO
import xml.etree.ElementTree as et
import time
from rdfchangesets import ChangeSet, BatchChangeSet
import json
import re
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
CS = Namespace("http://purl.org/vocab/changeset/schema#")

APIKEY_HEADER='X_KASABI_APIKEY'


def response_body_as_graph(response, body, format="n3"):
  g = Graph()
  if response.status in range (200,300):
    g.parse(StringInputSource(body), format=format)
  return (response, g)


class PytassiumError(Exception):
  pass

class KasabiApi:
  def __init__(self, uri, apikey, client=None):
    if client is None:
      self.client = httplib2.Http()
      self.client.follow_all_redirects = True
    else:
      self.client = client
    
    self.apikey = apikey
    self.uri = uri


class AttributionApi(KasabiApi):
  def get(self, raw=False):
    response, body = self.client.request("%s?output=json"%self.uri, "GET",headers={"accept" : "application/json", APIKEY_HEADER:self.apikey})
    if raw or response.status not in range(200, 300):
      return response, body
    else:
      data = json.loads(body)
      return response, data
    
class StatusApi(KasabiApi):
  def get(self, raw=False):
    response, body = self.client.request("%s?output=json"%self.uri, "GET",headers={"accept" : "application/json", APIKEY_HEADER:self.apikey})
    if raw or response.status not in range(200, 300):
      return response, body
    else:
      data = json.loads(body)
      return response, data

class SparqlApi(KasabiApi):
  def sparql(self, query, media_type):
    return self.client.request("%s?query=%s" % (self.uri, urllib.quote_plus(query)), "GET", headers={"accept" : media_type, APIKEY_HEADER:self.apikey})

  def describe(self, uri, raw = False):
    query = "describe <%s>" % uri
    (response, body) = self.sparql(query=query, media_type='text/turtle')
    if raw or response.status not in range(200, 300):
      return (response, body)
    else:
      return response_body_as_graph(response, body, format='text/turtle')

  def ask(self, query, raw = False):
    (response, body) = self.sparql(query=query, media_type='application/sparql-results+xml')
    if raw or response.status not in range(200, 300):
      return response, body
    else:
      tree = et.fromstring(body)
      boolean = tree.find("{http://www.w3.org/2005/sparql-results#}boolean")
      return response, boolean.text == "true"
  
  def select(self, query, raw = False):
    (response, body) = self.sparql(query=query, media_type='application/sparql-results+xml')
    if raw or response.status not in range(200, 300):
      return response, body
    else:
      tree = et.fromstring(body)
      head = tree.find("{http://www.w3.org/2005/sparql-results#}head")
      headers = [x.get("name") for x in head.findall("{http://www.w3.org/2005/sparql-results#}variable")]
      results = []
      for result in tree.find("{http://www.w3.org/2005/sparql-results#}results").findall("{http://www.w3.org/2005/sparql-results#}result"):
        d = {}
        for binding in result.findall("{http://www.w3.org/2005/sparql-results#}binding"):
          name = binding.get("name")
          value = None
          uri = binding.find("{http://www.w3.org/2005/sparql-results#}uri")
          if uri is None:
            literal = binding.find("{http://www.w3.org/2005/sparql-results#}literal")
            if literal is None:
              bnode = binding.find("{http://www.w3.org/2005/sparql-results#}bnode")
              if bnode is None:
                raise PytassiumError("SPARQL select result binding value is not a URI, Literal or BNode")
              else:
                value = BNode(bnode.text)
            else:
              value = Literal(literal.text)
          else:
            value = URIRef(uri.text)
          d[name] = value
        results.append(d)
      return response, (headers, results)
    return response, body


class SearchApi(KasabiApi):
  pass
  
class LookupApi(KasabiApi):
  def lookup(self, uri, raw = False):
    (response, body) = self.client.request("%s?about=%s" % (self.uri, urllib.quote_plus(uri)), "GET",headers={"accept" : "text/turtle", APIKEY_HEADER:self.apikey})
    if raw:
      return (response, body)
    else:
      return response_body_as_graph(response, body)

class AugmentationApi(KasabiApi):
  pass
class ReconciliationApi(KasabiApi):
  pass
class UpdateApi(KasabiApi):
  def store_data(self, data, graph_uri=None, media_type='text/turtle'):
    """Store some RDF in a graph associated with this dataset."""    
    if graph_uri is not None:
      raise PytassiumError("graph_uri not currently supported")

    return self.client.request(self.uri, "POST", body=data, headers={"accept" : "*/*", 'content-type':media_type, APIKEY_HEADER:self.apikey})

  def store_graph(self, g, graph_uri=None):
    """Store the contents of a Graph object in a graph associated with this dataset"""
    if graph_uri is not None:
      raise PytassiumError("graph_uri not currently supported")

    data = g.serialize(format='nt')
    return self.store_data(data, graph_uri,'text/turtle')

  def store_file(self, filename, graph_uri=None, media_type=None):
    """Store the contents of a File (file-like object) in a graph associated with this dataset
       The client does not support streaming submissions of data, so the stream will be fully read before data is submitted to the platform
       file:: an IO object      
    """
    if graph_uri is not None:
      raise PytassiumError("graph_uri not currently supported")

    file = open(filename, 'r')
    data = file.read()
    file.close()

    if not media_type:
      if filename.endswith('.nt') or filename.endswith('.ttl'):
        media_type = 'text/turtle'
      else:
        media_type = 'application/rdf+xml' # TODO: convert to ntriples
    
    return self.store_data(data, graph_uri, media_type)

  def apply_changeset(self, changeset, graph_uri=None):
    """Patch some RDF in a graph associated with this dataset."""    
    if graph_uri is not None:
      raise PytassiumError("graph_uri not currently supported")

    g = changeset.getGraph()
    data = g.serialize(format='xml')
    return self.client.request(self.uri, "POST", body=data, headers={"accept" : "*/*", 'content-type':'application/vnd.talis.changeset+xml', APIKEY_HEADER:self.apikey})

class JobsApi(KasabiApi):
  pass
  
  
class Dataset:
  api_map = {}
  service_types = {
    "http://rdfs.org/ns/void#sparqlEndpoint":("sparql",SparqlApi),
    "http://rdfs.org/ns/void#uriLookupEndpoint": ("lookup",LookupApi),
    "http://labs.kasabi.com/ns/services#searchEndpoint": ("search",SearchApi),
    "http://labs.kasabi.com/ns/services#augmentationEndpoint": ("augmentation",AugmentationApi),
    "http://labs.kasabi.com/ns/services#reconciliationEndpoint": ("reconciliation",ReconciliationApi),
    "http://labs.kasabi.com/ns/services#storeEndpoint": ("update",UpdateApi),
    "http://labs.kasabi.com/ns/services#statusEndpoint": ("status",StatusApi),
    "http://labs.kasabi.com/ns/services#jobsEndpoint": ("jobs",JobsApi),
    "http://labs.kasabi.com/ns/services#attributionEndpoint": ("attribution",AttributionApi),
  }

  def __init__(self, uri, apikey, client=None):
    if client is None:
      self.client = httplib2.Http()
      self.client.follow_all_redirects = True
    else:
      self.client = client
    
    self.apikey = apikey
    self.meta = None
    
    if uri.startswith("http://data.kasabi.com/dataset/"):
      self.uid = uri[31:]
      self.uri = uri
      
    else:
      self.uid = uri
      self.uri = "http://data.kasabi.com/dataset/" + uri


  def store_data(self, data, graph_uri=None, media_type='text/turtle'):
    api = self.get_api('update')
    if not api:
      raise PytassiumError("Dataset does not have an update api")
    return api.store_data(data=data, graph_uri=graph_uri, media_type=media_type)
  
  def store_file(self, filename, graph_uri=None, media_type=None):
    api = self.get_api('update')
    if not api:
      raise PytassiumError("Dataset does not have an update api")
    return api.store_file(filename, graph_uri=graph_uri, media_type=media_type)

  def store_graph(self, g, graph_uri=None):
    api = self.get_api('update')
    if not api:
      raise PytassiumError("Dataset does not have an update api")
    return api.store_graph(g, graph_uri=graph_uri)

  def apply_changeset(self, changeset, graph_uri=None):
    api = self.get_api('update')
    if not api:
      raise PytassiumError("Dataset does not have an update api")
    return api.apply_changeset(changeset, graph_uri=graph_uri)

  def lookup(self, uri, raw = False):
    api = self.get_api('lookup')
    if not api:
      raise PytassiumError("Dataset does not have a lookup api")
    return api.lookup(uri, raw)
    
  def describe(self, uri, raw = False):
    api = self.get_api('sparql')
    if not api:
      raise PytassiumError("Dataset does not have a sparql api")
    return api.describe(uri, raw)

  def sparql(self, query, media_type):
    api = self.get_api('sparql')
    if not api:
      raise PytassiumError("Dataset does not have a sparql api")
    return api.sparql(query, media_type)
  
  def ask(self, query, raw = False):
    api = self.get_api('sparql')
    if not api:
      raise PytassiumError("Dataset does not have a sparql api")
    return api.ask(query, raw)
  
  def select(self, query, raw = False):
    api = self.get_api('sparql')
    if not api:
      raise PytassiumError("Dataset does not have a sparql api")
    return api.select(query, raw)

  def attribution(self, raw = False):
    api = self.get_api('attribution')
    if not api:
      raise PytassiumError("Dataset does not have an attribution api")
    return api.get(raw)

  def status(self, raw = False):
    api = self.get_api('status')
    if not api:
      raise PytassiumError("Dataset does not have a status api")
    return api.get(raw)

  def fetch_meta(self):
    response, body = self.client.request("%s.ttl"%self.uri, "GET",headers={"accept" : "text/turtle", APIKEY_HEADER:self.apikey})
    response, self.meta = response_body_as_graph(response, body, format="n3")
    # Workaround for a bug in the beta. remove next line when fixed
    dataset_uri = re.sub('data.kasabi.com', 'beta.kasabi.com', self.uri)
    t = self.meta.triples((URIRef(dataset_uri),None,None))
    for (s,p,o) in t:
      if str(p) in self.service_types:
        short_name = self.service_types[str(p)][0]
        clazz = self.service_types[str(p)][1]
        api = clazz(str(o), self.apikey, self.client)
        if short_name not in self.api_map:
          self.api_map[short_name] = [api]
        else:
          self.api_map[short_name].append(api)

  def get_api(self, t):
    if self.meta is None:
      self.fetch_meta()
    
    if t in self.api_map:
      return self.api_map[t][0]
    else:
      return None 



  
