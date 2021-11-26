#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import gzip, traceback
from lib.parse_entities import parse_entities
from lib.search_entities import search_entities
from lib.disambiguate_entities import disambiguate_entities
from lib.parse_warc import get_html_warc, text_extract
from lib.text_cleaner import clean_text

OUTPUT_FILE = "sample_predictions.tsv"

def _parse_warc(_input):
    return parse_warc(_input)

def _parse_entities(raw_text):
    return parse_entities(raw_text)

def _search_entities(entities):
    return search_entities(entities)

def _disambiguate_entities(raw_text, wiki_entities, method = "naive"):
    return disambiguate_entities(raw_text, wiki_entities, method)

def _clean_text(raw_text):
    return clean_text(raw_text)

def write_result(file_pointer, entities, page_id):
    for wikiID, label, wikiLabel in entities:
        file_pointer.write(page_id + '\t' + label.replace("\n", "").replace("\t", "") + '\t' + wikiID + '\n')

if __name__ == '__main__':
    import sys
    try:
        _, INPUT = sys.argv
    except Exception as e:
        print('Usage: python starter-code.py INPUT')
        sys.exit(0)

    f = open(OUTPUT_FILE, 'w')
    # Parse INPUT WARC file
    for html_prase, page_id in get_html_warc(INPUT):
        try: 
            # Extract and clean HTML text 
            raw_text = text_extract(html_prase)
            raw_text = clean_text(raw_text)

            # Entity recognition
            entities = _parse_entities(raw_text)
            if (entities == None or len(entities) < 1):
                continue
            
            # Candidates generation
            wiki_entities = _search_entities(entities)
            if (wiki_entities == None or len(wiki_entities) < 1):
                continue

            # Candidates dissambiguation
            final_entities = _disambiguate_entities(raw_text, wiki_entities, "popularity")

            write_result(f, final_entities, page_id)

        except Exception as e:
            traceback.print_exc()
            print (e)
    f.close()