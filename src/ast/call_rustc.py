#!/usr/bin/python3

import json
import subprocess

def call_rustc(path):
    result = subprocess.run(['rustc', '-Z', 'ast-json', ('./rust/' + path)], \
                            stdout=subprocess.PIPE)
    ret = json.loads(result.stdout.decode('utf-8'))
    return ret
