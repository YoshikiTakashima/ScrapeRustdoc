#!/bin/bash
# Author: Yoshiki Takashima
# Project: Rust Compiler Testing
# Org: Carnegie Mellon CyLab

### Print Utility functions
err () {
    RED='\033[0;31m'
    NC='\033[0m'
    echo -e "${RED}$1${NC}"
}
usage () {
    err "Incorrect Parameters"
    echo './run.sh COMMAND URL'
    echo -e "\tCOMMAND: "
    echo -e "\t\tfiles:\tprint filenames associated with this module."
    echo -e "\t\ttypes:\tprint type signatures"
    echo -e "\t\tsypet:\tprint type signatures as Java SyPet code."

    echo ""
    echo -e "\tURL: URL of rust documentation online"
}

### Input Sanity checking
if [ "$#" -ne 2 ] ; then
    usage
    exit 1
fi

### Run corresponding python scripts
if [ "$1" = "files" ]; then
    python3 ./src/print_files.py "$2"
elif [ "$1" = "types" ]; then
    err "$1 not implemented" #python3 ./src/print_files.py "$2"
elif [ "$1" = "sypet" ]; then
    err "$1 not implemented" #python3 ./src/print_files.py "$2"
else
    usage
fi
