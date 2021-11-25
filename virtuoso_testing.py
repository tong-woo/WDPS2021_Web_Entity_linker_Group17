import urllib, json, requests

"""
This file demonstrates how to make a simple SPARQL query against the public
WikiData graph endpoint for the WDPS course.

Additional information:
- Simple SPARQL editor: http://fs0.das5.cs.vu.nl:10011/sparql
- Additional information http://fs0.das5.cs.vu.nl:10011/sparql/?help=intro
- Prefixes in the dataset: http://fs0.das5.cs.vu.nl:10011/sparql/?help=nsdecl
"""

HOST = "http://fs0.das5.cs.vu.nl:10011/sparql"

def sparqlQuery(query, format="application/json"):
    resp = requests.get(HOST + "?" + urllib.parse.urlencode({
        "default-graph": "",
        "should-sponge": "soft",
        "query": query,
        "debug": "on",
        "timeout": "",
        "format": format,
        "save": "display",
        "fname": ""
    }))
    print (resp.content.decode("utf-8"))
    return json.loads(resp.content.decode("utf-8"))


#query = "select distinct ?Concept where {[] a ?Concept} LIMIT 100"
#query = "SELECT ?p ?o WHERE {<http://www.wikidata.org/entity/Q70764476>} ?p ?o"
# query = """
# PREFIX entity: <http://www.wikidata.org/entity/>  
# SELECT ?propUrl ?propLabel ?valUrl ?valLabel
# WHERE 
#     { 	entity:Q1065414 ?propUrl ?valUrl . 		
#         ?property ?ref ?propUrl . 			
#         ?property rdfs:label ?propLabel . 	   	
#         ?valUrl rdfs:label ?valLabel 	
#         FILTER (LANG(?valLabel) = 'en') . 	
#         FILTER (lang(?propLabel) = 'en' ) 
#     } 
#         ORDER BY ?propUrl ?valUrl
# """
# query = """
# PREFIX entity: <http://www.wikidata.org/entity/>  
# SELECT ?verb1 WHERE {
#   entity:Q1065414 ?verb1 entity:Q2610973
# }
# """
# query = """
# PREFIX entity: <http://www.wikidata.org/entity/>  
# ASK {
#   entity:Q2610973 ((<>|!<>)|^(<>|!<>))* entity:Q1065414 
# }
# """

# FIND ALL RELATIONSHIPS BETWEEN TWO NODES
# Could be useful...
query = """ 
PREFIX wd: <http://www.wikidata.org/entity/>  
SELECT ?verb1 ?verb2 WHERE {
  wd:Q55 ?verb1 wd:Q727.
  wd:Q727 ?verb2 wd:Q55  
}
"""

# Get number of triplets of entity
query = """
PREFIX wd: <http://www.wikidata.org/entity/>  
SELECT *
WHERE 
{
  VALUES ?s {  wd:Q2610973  }
  ?s ?p ?o
}
"""

# query = """
#     PREFIX wd: <http://www.wikidata.org/entity/>  
#     PREFIX wdt: <http://www.wikidata.org/prop/direct/> 
#     select ?item where {
#         ?item wdt:P31 wd:Q5 .
#         VALUES ?item {  wd:Q352 }
#     }
# """

# Get number of triplets between two entities
query = """
PREFIX wd: <http://www.wikidata.org/entity/>  
SELECT (COUNT(*) as ?Triples) 
WHERE 
{
  VALUES ?s {  wd:Q2610973  }
  VALUES ?o {  wd:Q1065414 wd:Q1111  }
  ?s ?p ?o
}
"""

# RESULTS LENGTH = MORE POPULAR = CORRECT RESULTS
# 
data = sparqlQuery(query)
print (data)
print(json.dumps(data, indent=4))

a=1