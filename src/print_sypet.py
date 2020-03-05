#!/usr/bin/python3

class FunctionDef:
    def __init__(self, name, input_types, output_type): # Input: str, [str], [str]
        self._name = name
        self._input_types = self.__strip_str_list(input_types)
        self._output_type = self.__strip_str_list(output_type)

    def __strip_str_list(self, str_list):
        return list(map(lambda x: x.strip(), str_list))

    def get_name(self): # -> str
        return self._name

    def get_input(self): # -> [str]
        return self._input_types

    def get_output(self): # -> [str]
        return self._output_type

def print_sypet_type(type_def):
    print('petri.createType("{}");'.format(type_def))

def print_sypet_function(fn_def):
    name = fn_def.get_name()
    input0 = "()"
    output0 = "()"
    
    if len(fn_def.get_input()) > 0:
        input0 = fn_def.get_input()[0]
    if len(fn_def.get_output()) > 0:
        output0 = fn_def.get_output()[0]
    
    print('petri.createAPI("{}", "{}", "{}");'.format(name, input0, output0))


def function_list_to_sypet(fn_list):
    types = set([])
    for fn in fn_list:
        for tp in fn.get_input():
            types.add(tp)
        for tp in fn.get_output():
            types.add(tp)

    for tp in types:
        print_sypet_type(tp)

    for fn in fn_list:
        print_sypet_function(fn)

FUNCTIONS = []

STRINGS = [FunctionDef("std::string::String/::core::cmp::PartialOrd[String,String]/lt",
                       ["& String", "& String"], ["bool"]),
           FunctionDef("std::string::String/::core::cmp::PartialOrd[String,String]/le",
                       ["& String", "& String"], ["bool"]),
           FunctionDef("std::string::String/::core::cmp::PartialOrd[String,String]/gt",
                       ["& String", "& String"], ["bool"]),
           FunctionDef("std::string::String/::core::cmp::PartialOrd[String,String]/ge",
                       ["&String", "& String"], ["bool"]),
           FunctionDef("std::string::String/::core::cmp::PartialEq[String,FromUtf8Error]/ne",
                       ["& String", "& FromUtf8Error"], ["bool"]),
           FunctionDef("std::string::String/Pub/with_capacity",
                       ["usize"], ["String"]),
           FunctionDef("std::string::String/Pub/from_utf8",
                       ["Vec<u8>"], ["Result<String, FromUtf8Error>"]),
           FunctionDef("std::string::String/Pub/from_utf8_lossy",
                       ["& [u8]"], ["Cow<'_, str>"]),
           FunctionDef("std::string::String/Pub/from_utf16",
                       ["& [u16]"], ["Result<String, FromUtf16Error>"]),
           FunctionDef("std::string::String/Pub/from_utf16_lossy",
                       ["& [u16]"], ["String"]),
           FunctionDef("std::string::String/Pub/into_raw_parts",
                       ["String"], ["*mut u8", "usize", "usize"]),
           FunctionDef("std::string::String/Pub/into_bytes",
                       ["String"], ["Vec<u8>"]),
           FunctionDef("std::string::String/Pub/as_str",
                       ["String"], ["& str"]),
           FunctionDef("std::string::String/Pub/as_mut_str",
                       ["&mut String"], ["&mut str"]),
           FunctionDef("std::string::String/Pub/push_str",
                       ["&mut String"], ["&mut str"]),
           FunctionDef("std::string::String/Pub/capacity",
                       ["&String"], ["usize"]),
           FunctionDef("std::string::String/Pub/reserve",
                       ["&mut String", "usize"], []),
           FunctionDef("std::string::String/Pub/reserve_exact",
                       ["&mut String", "usize"], []),
           FunctionDef("std::string::String/Pub/try_reserve",
                       ["&mut String", "usize"], ["Result<(), TryReserveError>"]),
           FunctionDef("std::string::String/Pub/try_reserve_exact",
                       ["&mut String", "usize"], ["Result<(), TryReserveError>"]),
           FunctionDef("std::string::String/Pub/shrink_to_fit",
                       ["&mut String"], []),
           FunctionDef("std::string::String/Pub/shrink_to",
                       ["&mut String", "usize"], []),
           FunctionDef("std::string::String/Pub/push",
                       ["&mut String", "char"], []),
           FunctionDef("std::string::String/Pub/as_bytes",
                       ["& String", ], ["& [u8]"]),
           FunctionDef("std::string::String/Pub/truncate",
                       ["&mut String" ], ["usize"]),
           FunctionDef("std::string::String/Pub/pop",
                       ["&mut String" ], ["Option<char>"]),
           FunctionDef("std::string::String/Pub/remove",
                       ["&mut String", "usize" ], ["char"]),
           FunctionDef("std::string::String/Pub/retain<F>",
                       ["&mut String", "FnMut(char) -> bool" ], ["bool"]),
           FunctionDef("std::string::String/Pub/insert",
                       ["&mut String", "usize", "char" ], []),
           FunctionDef("std::string::String/Pub/insert_str",
                       ["&mut String", "usize", "& str" ], []),
           FunctionDef("std::string::String/Pub/len",
                       ["& String" ], ["usize"]),
           FunctionDef("std::string::String/Pub/is_empty",
                       ["& String" ], ["bool"]),
           FunctionDef("std::string::String/Pub/split_off",
                       ["&mut String", "usize" ], ["String"]),
           FunctionDef("std::string::String/Pub/clear",
                       ["&mut String"], []),
           FunctionDef("std::string::String/Pub/drain",
                       ["&mut String", "RangeBounds<usize>"], ["Drain<'_> where"]),
           FunctionDef("std::string::String/Pub/replace_range",
                       ["&mut String", "RangeBounds<usize>", "& str"], []),
           FunctionDef("std::string::String/Pub/into_boxed_str",
                       ["&mut String"], ["Box<str>"]),
           FunctionDef("std::string::FromUtf8Error/Pub/into_bytes",
                       ["FromUtf8Error"], ["Vec<u8>"]),
           FunctionDef("std::string::FromUtf8Error/Pub/utf8_error",
                       ["& FromUtf8Error"], ["Utf8Error"]),
           FunctionDef("std::string::String/Pub/clone_from",
                       ["& String", "& String"], []),
           FunctionDef("std::string::String/std::str::pattern::Pattern[String,str]/into_searcher",
                       ["& String", "& str"], ["<&'b str as Pattern<'a>>::Searcher"]),
           FunctionDef("std::string::String/std::str::pattern::Pattern[String,str]/is_contained_in",
                       ["& String", "& str"], ["bool"]),
           FunctionDef("std::string::String/std::str::pattern::Pattern[String,str]/prefix_of",
                       ["& String", "& str"], ["bool"]),
           FunctionDef("std::string::String/::core::cmp::PartialEq[String,String]/ne",
                       ["& String", "& String"], ["bool"]),
           FunctionDef("std::string::String/::core::cmp::PartialEq[String,str]/ne",
                       ["& String", "& str"], ["bool"]),
           FunctionDef("std::str/::core::cmp::PartialEq[str,String]/ne",
                       ["& str", "& String"], ["bool"]),
           FunctionDef("std::str/::core::cmp::PartialEq[str,Cow]/ne",
                       [ "& String" ], ["<Cow<'a, str>"]),
           FunctionDef("std::string::String/::core::ops::Add[String,str]/add",
                       [ "& String", "& str" ], ["String"]),
           FunctionDef("std::string::String/::core::ops::Deref[String]/deref",
                       [ "& String" ], ["& str"]),
           FunctionDef("std::string::String/ops::Index<ops::Range<usize>>[String]/index",
                       [ "& String", "ops::Range<usize>" ], ["& str"]),
           FunctionDef("std::string::String/ops::Index<ops::RangeTo<usize>>[String]/index",
                       [ "& String", "ops::RangeTo<usize>" ], ["& str"]),
           FunctionDef("std::string::String/ops::Index<ops::RangeFrom<usize>>[String]/index",
                       [ "& String", "ops::RangeFrom<usize>" ], ["& str"]),
           FunctionDef("std::string::String/ops::Index<ops::RangeFull>[String]/index",
                       [ "& String", "ops::RangeFull" ], ["& str"]),
           FunctionDef("std::string::String/ops::Index<ops::RangeInclusive<usize>>[String]/index",
                       [ "& String", "ops::RangeInclusive<usize>" ], ["& str"]),
           FunctionDef("std::string::String/ops::Index<ops::RangeToInclusive<usize>>[String]/index",
                       [ "& String", "ops::RangeToInclusive<usize>" ], ["& str"]),
           FunctionDef("std::string::String/std::str::FromStr[String]/index",
                       [ "& str" ], ["Result<String, Self::Err>"]),
           FunctionDef("std::string::String/std::str::FromStr[String]/write_char",
                       [ "String", "char" ], ["std::fmt::Result"]),
           FunctionDef("std::string::String/std::borrow::Borrow[String]/borrow",
                       [ "String"], ["& String"]),
           FunctionDef("std::string::String/std::borrow::BorrowMut[String]/borrow_mut",
                       [ "String"], ["&mut String"])
]


FUNCTIONS = FUNCTIONS + STRINGS
if __name__ == "__main__":
    function_list_to_sypet(FUNCTIONS)
