#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import os
import gzip
import re
import urllib
import requests
from io import BytesIO
from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup

def isurl(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return True if re.match(regex,url) else False

# Generator of HTMLs from a warcfile 
def get_html_warc(warcfile):
    '''
    读取CommonCrawl的warc\wet文件，返回html,

    Args:
        pathfile：CommonCrawl的warc、wet格式文件或url字符串,warc,wet文件为gzip压缩格式
    Returns:
        A string of html
    '''
    #判断参数是否为url
    if isurl(warcfile):
        resp = requests.get(warcfile, stream=True)
        f=resp.raw
    else:
        f = gzip.open(warcfile,'rb')
    for record in ArchiveIterator(f):
        #page_id = record.rec_headers.get_header('WARC-Record-ID')
        #print(page_id)
        page_id = record.rec_headers.get_header('WARC-TREC-ID')
        print(page_id)
        if record.rec_type == 'warcinfo':
            warcinfo=record.raw_stream.read()
        #get warc file content\
        elif record.rec_type == 'response':
            content_type=record.http_headers.get_header('Content-Type')
            if content_type and content_type[:9] == 'text/html':
                # get html charset
                strlist=content_type.replace(' ', '').lower().split(';')
                if len(strlist)>1:
                    if strlist[1][:8]=='charset=':
                        charset=strlist[1][8:]
                    else:
                        charset=strlist[1]
                else: #no charset
                    charset='utf-8'
                payload = record.content_stream().read().decode(encoding=charset,errors= 'ignore')
                yield [payload, page_id]
            elif content_type and content_type[:19] == 'application/rss+xml':
                #process xml type
                xml=record.content_stream().read()
            elif content_type == 'application/pdf' :
                #process pdf type
                pdf=record.content_stream().read()
            else:
                #other type
                pass 
        #get wet file content         
        elif record.rec_type == 'conversion':
            payload=record.content_stream().read().decode(encoding=charset,errors= 'ignore')
            yield [payload, page_id]
    if not isurl(warcfile):
        f.close()

 
# Extract text from HTML tree using beautifoul soup
def text_extract(html_prase):
    output=''
    soup= BeautifulSoup(html_prase,'lxml')
    body= soup.body
    if body is None:
        return None
    for tag in body.select('script'):
        tag.decompose()
    for tag in body.select('style'):
        tag.decompose()

    text = body.get_text(separator='')
    return text

def save_to_file(file_name,contents):
    file =open(file_name,'w+')
    file.write(contents)
    file.close()

# Parse a warc file into HTML text
def parse_warc(location):
    html_prase = get_html_warc(location)
    text = text_extract(html_prase)
    return text
