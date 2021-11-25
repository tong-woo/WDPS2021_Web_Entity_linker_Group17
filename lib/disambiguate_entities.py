import urllib, json, requests, json, traceback

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
    #print (resp.content.decode("utf-8"))
    return json.loads(resp.content.decode("utf-8"))


def get_popularity(wikiID):
    # Get number of triplets of entity
    entityId = wikiID.replace('>', '').split('/')[-1]
    query = """
        PREFIX wd: <http://www.wikidata.org/entity/>  
        SELECT (COUNT(*) as ?Triples) 
        WHERE {
            VALUES ?s {  wd:""" + entityId + """ }
            ?s ?p ?o
        }
    """
    try:
        results = int(sparqlQuery(query)["results"]["bindings"][0]["Triples"]["value"])
        return results
    except Exception as e:
        print (e)
        traceback.print_exc()
        return 0

def get_connections(wikiID1, wikiIDs):
    entityId1 = wikiID1.replace('>', '').split('/')[-1]
    wikiIDs_formatted = []
    for wikiId in wikiIDs:
        entityId = "wd:" + wikiId.replace('>', '').split('/')[-1]
        wikiIDs_formatted.append(entityId)
    query = """
        PREFIX wd: <http://www.wikidata.org/entity/>  
        SELECT (COUNT(*) as ?Triples) 
        WHERE {
            VALUES ?s {  wd:""" + entityId1 + """ }
            VALUES ?o {  """ + " ".join(wikiIDs_formatted) + """ }
            ?s ?p ?o
        }
    """
    try:
        results = int(sparqlQuery(query)["results"]["bindings"][0]["Triples"]["value"])
        return results
    except Exception as e:
        print (e)
        traceback.print_exc()
        return 0

def checkIfPerson(wikiID):
    entityId = wikiID.replace('>', '').split('/')[-1]
    query = """
        PREFIX wd: <http://www.wikidata.org/entity/>  
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>
        select ?item where {
            ?item wdt:P31 wd:Q5 . 
            VALUES ?item {  wd:""" + entityId + """ }
        }
    """
    try:
        results = len(sparqlQuery(query)["results"]["bindings"])
        return results
    except Exception as e:
        print (e)
        traceback.print_exc()
        return 0

def disambiguate_entities(raw_text, entities, method = "naive"):
    found_entities = []
    if method == "naive":
        for entityLocalId, entity in entities.items():
            for wikiID, label, score, original_label, label_type in entity:
                found_entities.append([wikiID, original_label, label])
                break
    else:
        # For each entity
        for entityLocalId, entity in entities.items():
            found = 0
            disambiguate_rankings = {}

            # For each candidate of the entity
            for wikiID, label, score, original_label, label_type in entity:
                # If the entity is a PERSON we can easily remove candidates
                # if label_type == 'PERSON':
                #     if checkIfPerson(wikiID) < 1:
                #         continue

                # Initiate ranking for entity
                if label not in disambiguate_rankings:
                    disambiguate_rankings[label] = {
                        "popularity": 0,
                        "relations": 0,
                        "info": [wikiID, label, score, original_label]
                    }

                # If we have already found entities
                if len(found_entities) > 0:
                    # Same context assumption search
                    for wikiID_tmp, label_tmp, es_tmp_label in found_entities:
                        # Same context assumption
                        if (label_tmp == original_label):
                            found_entities.append([wikiID, original_label, label])
                            found = 1
                            break
                    if found == 1:
                        break

                    # Search for connections with already found entities
                    found_wiki_ids = []
                    for wikiID_tmp, label_tmp, es_tmp_label in found_entities:
                        found_wiki_ids.append(wikiID_tmp)
                    local_connections = get_connections(wikiID, found_wiki_ids)
                    disambiguate_rankings[label]["relations"] += local_connections

                # Calculate entity popularity
                entity_popularity = get_popularity(wikiID)
                disambiguate_rankings[label]["popularity"] = entity_popularity

            # No candidates
            if (len(disambiguate_rankings) < 1):
                continue

            #print ('RANKING RAW', disambiguate_rankings)

            # Sorting candidates by their scores of popularity and connections with other found entities
            sort_ranking_popularity = list(dict(sorted(disambiguate_rankings.items(), key=lambda item: item[1]["popularity"])).values())
            sort_ranking_connections = list(dict(sorted(disambiguate_rankings.items(), key=lambda item: item[1]["relations"])).values())

            #print('SORTED RANKING', sort_ranking_popularity)

            # Best ranked in terms of popularity
            best_ranked_entity = sort_ranking_popularity[-1]["info"]
            # If there are relations with already foudn entities, we prioritize this ranking over popularity
            if (sort_ranking_connections[-1]["relations"] > 0):
                best_ranked_entity = sort_ranking_connections[-1]["info"]

            print(best_ranked_entity)
            found_entities.append([best_ranked_entity[0], best_ranked_entity[-1], best_ranked_entity[1]])
    return found_entities