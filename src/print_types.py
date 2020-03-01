#!/usr/bin/python3

from .print_files import get_files
from .ast import call_rustc



if __name__ == "__main__":
    from sys import argv
    paths = from_raw(argv[1])
    exit(0)
