#!/usr/bin/python3
import re

def _extract_headers(raw, targets):    
    ret = []
    #find next instance of target word (make sure non-negative index)
    start = 0
    start = start + min(map(lambda tgt: len(raw) if raw[start:].find(tgt) < 0 \
                                else raw[start:].find(tgt), \
                                targets))+1
    while(start < len(raw)):
        # Find the end of decl
        block_start = start
        while block_start < len(raw) and raw[block_start] != '{' and raw[block_start] != ';' :
            block_start += 1

        # Find the end of text block
        end = block_start+1
        ctr = 1
        while ctr > 0 and end < len(raw):
            if raw[end] == '{':
                ctr += 1
            elif raw[end] == '}':
                ctr -= 1
            end += 1
        if raw[block_start] == ';':
            end = block_start+1

        #identify block type
        kind = ""
        for tgt in targets:
            if tgt[1:] == raw[start:start+(len(tgt)-1)]:
                kind = tgt.strip()

        # 
        ret.append({
            "kind": kind,
            "decl": raw[start:block_start].strip(),
            "body": raw[block_start+1:end-1].strip()
        })
        
        start = end
        start = start + min(map(lambda tgt: len(raw) if raw[start:].find(tgt) < 0 \
                                else raw[start:].find(tgt), \
                                targets))+1
    return ret

# Search inside implementation
def _search_impl(hdr):
    IMPL_TARGETS = ["\npub fn ",
                    "\nfn ",
                    "\ntype "]
    impls = _extract_headers(hdr['body'], IMPL_TARGETS)
    for i in impls:
        i['parent'] = hdr['decl']
        if i["kind"] == "pub fn":
           i["kind"] = "fn"
    return impls

## Parsers for object struct/enum
def _parse_struct_decl(decl):
    obj = decl.split("struct")[1]
    return obj.strip()
def _parse_enum_decl(decl):
    obj = decl.split("enum")[1]
    return obj.strip()

def _parse_impl(impl_decl):
    KEYWORD_TGT = "for"
    KEYWORD_TRAIT = "impl"
    ret = {}
    trait_index = impl_decl.find(KEYWORD_TRAIT) + len(KEYWORD_TRAIT)
    target_index_if_exist = impl_decl.find(KEYWORD_TGT)
    if target_index_if_exist > trait_index: # case: impl "trait" for "object"
        ret['trait'] = impl_decl[trait_index:target_index_if_exist].strip()
        ret['object'] = impl_decl[target_index_if_exist+len(KEYWORD_TGT):].strip()
    else:                                   # case: impl "object"
        ret['trait'] = ''
        ret['object'] = impl_decl[trait_index:].strip()
    return ret

## Parsers for full functions.
## Requires function dictionary map and trait context
def _parse_function(fn):
    return {}
        
# Simple file reader: filepath -> content
#   If the file is read, then eliminate whitespace
def _read_file(path):
    with open(path,'r') as fp:
        content = fp.read().split('\n')
        content = map(lambda line: line.strip(), content)
        content = filter(lambda line: not (re.search("^#", line) or re.search("^//", line)), \
                         content)
        return "\n".join(content)
    #If file open fails, then
    return ""

def sig_from_raw(raw_path):
    min_raw = _read_file(raw_path)
    if len(min_raw) == 0:
        return {}, []
    
    

# END OF LIBRARY------------------------
# Debug stuff below
def _print_header(hdr, params):
    for p in params:
        print("{}: {}".format(p, hdr[p]))
    print("-----------------------------")

# Mini test interface
if __name__ == "__main__":
    from sys import argv
    min_raw = _read_file(argv[1])
    HL_TARGETS = ["\npub struct ",
                  "\npub enum ",
                  "\nimpl ",
                  "\nimpl<",
                  "\nfn ",
                  "\npub trait " ]
    headers = _extract_headers(min_raw, HL_TARGETS)
    for hdr in headers:
        if hdr["kind"] == "pub struct":
            hdr["kind"] = "struct"
        elif hdr["kind"] == "pub enum":
            hdr["kind"] = "enum"
        elif hdr["kind"] == "impl<":
            hdr["kind"] = "impl"
        elif hdr["kind"] == "pub trait":
            hdr["kind"] = "trait"
    
    types = set()
    functions = []
    for hdr in headers:
        #_print_header(hdr, ['kind', 'decl'])
        if hdr["kind"] == "struct":
            types.add(_parse_struct_decl(hdr['decl']))
        elif hdr["kind"] == "enum":
            types.add(_parse_enum_decl(hdr['decl']))
        elif hdr["kind"] == "impl":
            fns_impl = _search_impl(hdr)
            impl_decl_parsed = _parse_impl(hdr['decl'])
            _print_header(impl_decl_parsed, ['trait', 'object'])
            for fn in fns_impl:
                #_print_header(fn, ['kind', 'decl', 'parent'])
                fn_decl_parsed = _parse_function(fn) # parse function decl
                # add types
                # append functions
                pass
    
    #for t in types:
    #    print(t)
    #print("-----------------------------")
    #for f in functions:
    #    print(f)
            

    
