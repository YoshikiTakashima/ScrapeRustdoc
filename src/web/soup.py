#!/usr/bin/python3

from bs4 import BeautifulSoup

# _convert_url_to_filepath: string url -> string path
# Converts embedded source url into filepath in the rust source
def _convert_url_to_filepath(url):
    start = int(url.find("src/")) + len("src/")
    end = int(url.rfind(".html"))
    
    if start < 0 or start >= end :
        return ""
    return "src/lib" + url[start:end]

# get_source_files string text -> [string paths]
# parses html document and gets all the source links
def get_source_filepaths(text):
    soup = BeautifulSoup(text, 'html.parser')
    srclinks = map(lambda a: _convert_url_to_filepath(a['href']), \
                  soup.findAll("a", {"class": "srclink"}))
    srclinks = list(dict.fromkeys(srclinks)) #Dedup
    return filter(lambda s: len(s) > 0, srclinks)
