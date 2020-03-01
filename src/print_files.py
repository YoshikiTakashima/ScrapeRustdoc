#!/usr/bin/python3

from web import fetch
from web import get_source_filepaths
from sys import argv

def get_files(url):
    doc_html = fetch(url)
    return get_source_filepaths(doc_html)

if __name__ == "__main__":
    for path in get_files(argv[1]):
        print(path)
    exit(0)
