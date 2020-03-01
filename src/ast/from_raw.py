#!/usr/bin/python3

def _extract_headers(raw):
    # Targets to find in text
    TARGETS = ["\nstruct ",
               "\nenum ",
               "\nimpl ",
               "\nfn ",
               "\ntrait " ]
    ret = []
    #find next instance of target word (make sure non-negative index)
    start = 0
    start = start + min(map(lambda tgt: len(raw) if raw[start:].find(tgt) < 0 \
                                else raw[start:].find(tgt), \
                                TARGETS)) + 1
    while(start < len(raw)):
        block_start = start
        while block_start < len(raw) and raw[block_start] != '{':
            block_start += 1

        #Find end of block
        end = block_start+1
        ctr = 1
        while ctr > 0 and end < len(raw):
            if raw[end] == '{':
                ctr += 1
            elif raw[end] == '}':
                ctr -= 1
            end += 1

        kind = ""
        if raw[start] == 's': #struct
            kind = "struct"
        elif raw[start] == 'e': #enum
            kind = "enum"
        elif raw[start] == 'i': #impl
            kind = "impl"
        elif raw[start] == 'f': #fn
            kind = "fn"
        elif raw[start] == 't': #trait
            kind = "trait"
        
        ret.append({
            "kind": kind,
            "decl": raw[start:block_start],
            "body": raw[block_start+1:end-1]
        })
        start = start + min(map(lambda tgt: len(raw) if raw[start:].find(tgt) < 0 \
                                else raw[start:].find(tgt), \
                                TARGETS)) + 1
    return ret

        
# Simple file reader: filepath -> content
#   If the file is read, then eliminate whitespace
def _read_file(path):
    with open(path,'r') as fp:
        content = fp.read()
        content = "\n".join(map(lambda line: line.strip(), \
                                content.split('\n')))
        return content
    #If file open fails, then
    return ""

def sig_from_raw(raw_path):
    program_txt = _read_file(raw_path)
    if len(program_txt) == 0:
        return {}, []

# Mini test interface
if __name__ == "__main__":
    from sys import argv
    #print(argv[1])
    min_raw = _read_file(argv[1])
    #print(min_raw)
    headers = _extract_headers(min_raw)
    for hdr in headers:
        print("kind: {}".format(hdr["kind"]))
        print("decl: {}".format(hdr["decl"]))
        print("Body:\n{}".format(hdr["body"]))
        print("-----------------------------")
