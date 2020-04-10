#!/usr/bin/python3
import json

class FunctionDef:
    def __init__(self, name, input_types, output_type): # Input: str, [str], [str]
        self._name = name
        self._input_types = self.__strip_str_list(input_types)
        self._output_type = output_type.strip()

    def __strip_str_list(self, str_list):
        return list(map(lambda x: x.strip(), str_list))

    def get_name(self): # -> str
        return self._name

    def get_input(self): # -> [str]
        return self._input_types

    def get_output(self): # -> str
        return self._output_type

def print_sypet_type(type_def):
    print('petri.createType("{}");'.format(type_def))

def print_sypet_function(fn_def):
    #List<Pair<String, Integer>> inputs
    print("inputs = new ArrayList<Pair<String, Integer>>();")
    name = fn_def.get_name()
    input_type_str = '"void"'
    output_type = fn_def.get_output()

    input_count = dict()
    for tp in fn_def.get_input():
        if tp not in input_count.keys():
            input_count[tp] = 1
        else:
            input_count[tp] = input_count[tp] + 1
    if  len(input_count.keys()) > 0:
        types = []
        for tp in input_count.keys():
            print('inputs.add(new ImmutablePair<String, Integer>("{}", new Integer({})));'.format(tp, input_count[tp]))
        input_type_str = "inputs"
    
    print('petri.createAPI("{}", {}, "{}");'.format(name, input_type_str, output_type))


def function_list_to_sypet(fn_list):
    print("List<Pair<String, Integer>> inputs;")
    types = set(["void"])
    for fn in fn_list:
        for tp in fn.get_input():
            types.add(tp)
        types.add(fn.get_output())

    for tp in types:
        print_sypet_type(tp)

    for fn in fn_list:
        print_sypet_function(fn)

def function_list_to_json(fn_list):
    ctr = 0
    obj_list = []
    for fn in fn_list:
        fn_obj = {}
        fn_obj['trait'] = ''
        fn_obj['dup'] = ctr
        parts = fn.get_name().split('/')
        fn_obj['path'] = parts[0] + '::' + parts[len(parts) - 1]
        fn_obj['kind'] = 'static' if ('/Static/' in fn.get_name()) else 'non-static'
        fn_obj['output'] = fn.get_output()
        fn_obj['inputs'] = ', '.join(fn.get_input())
        obj_list.append(fn_obj)
        ctr += 1
    print(json.dumps(obj_list))
        
FUNCTIONS = []

STRINGS = [FunctionDef("std::string::String/core::cmp::PartialOrd[String,String]/lt",
                       ["& String", "& String"], "bool"),
           FunctionDef("std::string::String/core::cmp::PartialOrd[String,String]/le",
                       ["& String", "& String"], "bool"),
           FunctionDef("std::string::String/core::cmp::PartialOrd[String,String]/gt",
                       ["& String", "& String"], "bool"),
           FunctionDef("std::string::String/core::cmp::PartialOrd[String,String]/ge",
                       ["& String", "& String"], "bool"),
           FunctionDef("std::string::String/core::cmp::PartialEq[String,FromUtf8Error]/ne",
                       ["& String", "& FromUtf8Error"], "bool"),
           FunctionDef("std::string::String/Static/new",
                       [], "String"),
           FunctionDef("std::string::String/Static/with_capacity",
                       ["usize"], "String"),
           FunctionDef("std::string::String/Static/from_utf8",
                       ["Vec<u8>"], "Result<String, FromUtf8Error>"),
           FunctionDef("std::string::String/Static/from_utf8_lossy",
                       ["& [u8]"], "Cow<'a, str>"),
           FunctionDef("std::string::String/Static/from_utf16",
                       ["& [u16]"], "Result<String, FromUtf16Error>"),
           FunctionDef("std::string::String/Static/from_utf16_lossy",
                       ["& [u16]"], "String"),
           FunctionDef("std::string::String/Pub/into_raw_parts",
                       ["String"], "(*mut u8, usize, usize)"),
           FunctionDef("std::string::String/Pub/into_bytes",
                       ["String"], "Vec<u8>"),
           FunctionDef("std::string::String/Pub/as_str",
                       ["String"], "& str"),
           FunctionDef("std::string::String/Pub/as_mut_str",
                       ["&mut String"], "&mut str"),
           FunctionDef("std::string::String/Pub/push_str",
                       ["&mut String"], "&mut str"),
           FunctionDef("std::string::String/Pub/capacity",
                       ["& String"], "usize"),
           FunctionDef("std::string::String/Pub/reserve",
                       ["&mut String", "usize"], "void"),
           FunctionDef("std::string::String/Pub/reserve_exact",
                       ["&mut String", "usize"], "void"),
           FunctionDef("std::string::String/Pub/try_reserve",
                       ["&mut String", "usize"], "Result<void, TryReserveError>"),
           FunctionDef("std::string::String/Pub/try_reserve_exact",
                       ["&mut String", "usize"], "Result<void, TryReserveError>"),
           FunctionDef("std::string::String/Pub/shrink_to_fit",
                       ["&mut String"], "void"),
           FunctionDef("std::string::String/Pub/shrink_to",
                       ["&mut String", "usize"], "void"),
           FunctionDef("std::string::String/Pub/push",
                       ["&mut String", "char"], "void"),
           FunctionDef("std::string::String/Pub/as_bytes",
                       ["& String", ], "& [u8]"),
           FunctionDef("std::string::String/Pub/truncate",
                       ["&mut String" ], "usize"),
           FunctionDef("std::string::String/Pub/pop",
                       ["&mut String" ], "Option<char>"),
           FunctionDef("std::string::String/Pub/remove",
                       ["&mut String", "usize" ], "char"),
           FunctionDef("std::string::String/Pub/retain<F>",
                       ["&mut String", "FnMut(char) -> bool" ], "bool"),
           FunctionDef("std::string::String/Pub/insert",
                       ["&mut String", "usize", "char" ], "void"),
           FunctionDef("std::string::String/Pub/insert_str",
                       ["&mut String", "usize", "& str" ], "void"),
           FunctionDef("std::string::String/Pub/len",
                       ["& String" ], "usize"),
           FunctionDef("std::string::String/Pub/is_empty",
                       ["& String" ], "bool"),
           FunctionDef("std::string::String/Pub/split_off",
                       ["&mut String", "usize" ], "String"),
           FunctionDef("std::string::String/Pub/clear",
                       ["&mut String"], "void"),
           FunctionDef("std::string::String/Pub/drain",
                       ["&mut String", "RangeBounds<usize>"], "Drain<'_>"),
           FunctionDef("std::string::String/Pub/replace_range",
                       ["&mut String", "RangeBounds<usize>", "& str"], "void"),
           FunctionDef("std::string::String/Pub/into_boxed_str",
                       ["&mut String"], "Box<str>"),
           FunctionDef("std::string::FromUtf8Error/Pub/into_bytes",
                       ["FromUtf8Error"], "Vec<u8>"),
           FunctionDef("std::string::FromUtf8Error/Pub/utf8_error",
                       ["& FromUtf8Error"], "Utf8Error"),
           FunctionDef("std::string::String/Pub/clone_from",
                       ["&mut String", "& String"], "void"),
           FunctionDef("std::string::String/std::str::pattern::Pattern[String,str]/into_searcher",
                       ["& String", "& str"], "<&'b str as Pattern<'a>>::Searcher"),
           FunctionDef("std::string::String/std::str::pattern::Pattern[String,str]/is_contained_in",
                       ["& String", "& str"], "bool"),
           FunctionDef("std::string::String/std::str::pattern::Pattern[String,str]/prefix_of",
                       ["& String", "& str"], "bool"),
           FunctionDef("std::string::String/core::cmp::PartialEq[String,String]/ne",
                       ["& String", "& String"], "bool"),
           FunctionDef("std::string::String/core::cmp::PartialEq[String,str]/ne",
                       ["& String", "& str"], "bool"),
           FunctionDef("std::str/core::cmp::PartialEq[str,String]/ne",
                       ["& str", "& String"], "bool"),
           FunctionDef("std::str/core::cmp::PartialEq[str,Cow]/ne",
                       [ "& String" ], "Cow<'a, str>"),
           FunctionDef("std::string::String/core::ops::Add[String,str]/add", 
                       [ "&mut String", "& str" ], "String"),
           FunctionDef("std::string::String/core::ops::Deref[String]/deref",
                       [ "& String" ], "& str"),
           FunctionDef("std::string::String/std::ops::Index<ops::Range<usize>>[String]/index",
                       [ "& String", "ops::Range<usize>" ], "& str"),
           FunctionDef("std::string::String/std::ops::Index<ops::RangeTo<usize>>[String]/index",
                       [ "& String", "ops::RangeTo<usize>" ], "& str"),
           FunctionDef("std::string::String/std::ops::Index<ops::RangeFrom<usize>>[String]/index",
                       [ "& String", "ops::RangeFrom<usize>" ], "& str"),
           FunctionDef("std::string::String/std::ops::Index<ops::RangeFull>[String]/index",
                       [ "& String", "std::ops::RangeFull" ], "& str"),
           FunctionDef("std::string::String/std::ops::Index<ops::RangeInclusive<usize>>[String]/index",
                       [ "& String", "ops::RangeInclusive<usize>" ], "& str"),
           FunctionDef("std::string::String/std::ops::Index<ops::RangeToInclusive<usize>>[String]/index",
                       [ "& String", "ops::RangeToInclusive<usize>" ], "& str"),
           FunctionDef("std::string::String/Static/std::str::FromStr[String]/from_str",
                       [ "& str" ], "Result<String, ParseError>"),
           FunctionDef("std::string::String/std::str::FromStr[String]/write_char",
                       [ "String", "char" ], "std::fmt::Result"),
           FunctionDef("std::string::String/std::borrow::Borrow[String]/borrow",
                       [ "String"], "& String"),
           FunctionDef("std::string::String/std::borrow::BorrowMut[String]/borrow_mut",
                       [ "mut String"], "&mut String"),
           FunctionDef("std::string::Fromutf8Error/std::borrow::Borrow[FromUtf8Error]/borrow",
                       [ "Fromutf8Error"], "& FromUtf8Error"),
           FunctionDef("std::string::String/std::borrow::Borrow[str]/borrow",
                       [ "str" ], "& str")
]

USIZE = []

FUNCTIONS = FUNCTIONS + STRINGS + USIZE
#print(len(FUNCTIONS))
if __name__ == "__main__":
    #function_list_to_sypet(FUNCTIONS)
    function_list_to_json(FUNCTIONS)
