#   Foma: a finite-state toolkit and library.
#   Copyright © 2008-2015 Mans Hulden
#   Copyright © 2023 Achievement Unlocked Inc., dba CultureFoundry
#
#   This file is part of foma.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

# When doing `from foma_bindings import *`, only import foma_bindings and foma_bindings.fst.
all = ['fst']

from ctypes import cdll, c_char, c_int, c_longlong, c_void_p, c_char_p, POINTER, Structure
from ctypes.util import find_library

foma_library_path = find_library('foma')
foma = cdll.LoadLibrary(foma_library_path)

EPSILON_SYMBOL = '□'

class FstStruct(Structure):
    _fields_ = [
        ("name", c_char * 40),
        ("arity", c_int),
        ("arccount", c_int),
        ("statecount", c_int),
        ("linecount", c_int),
        ("finalcount", c_int),
        ("pathcount", c_longlong),
        ("is_deterministic", c_int),
        ("is_pruned", c_int),
        ("is_minimized", c_int),
        ("is_epsilon_free", c_int),
        ("is_loop_free", c_int),
        ("is_completed", c_int),
        ("arcs_sorted_in", c_int),
        ("arcs_sorted_out", c_int),
        ("fsm_state", c_void_p),
        ("sigma", c_void_p),
        ("medlookup", c_void_p)
    ]

# FST functions.
foma_fsm_complement = foma.fsm_complement
foma_fsm_complement.restype = POINTER(FstStruct)
foma_fsm_compose = foma.fsm_compose
foma_fsm_compose.restype = POINTER(FstStruct)
foma_fsm_concat = foma.fsm_concat
foma_fsm_concat.restype = POINTER(FstStruct)
foma_fsm_copy = foma.fsm_copy
foma_fsm_copy.restype = POINTER(FstStruct)
foma_fsm_count = foma.fsm_count
foma_fsm_destroy = foma.fsm_destroy
foma_fsm_equivalent = foma.fsm_equivalent
foma_fsm_equivalent.restype = c_int
foma_fsm_flatten = foma.fsm_flatten
foma_fsm_flatten.restype = POINTER(FstStruct)
foma_fsm_intersect = foma.fsm_intersect
foma_fsm_intersect.restype = POINTER(FstStruct)
foma_fsm_isempty = foma.fsm_isempty
foma_fsm_isempty.restype = c_int
foma_fsm_lower = foma.fsm_lower
foma_fsm_lower.restype = POINTER(FstStruct)
foma_fsm_minimize = foma.fsm_minimize
foma_fsm_minimize.restype = POINTER(FstStruct)
foma_fsm_minus = foma.fsm_minus
foma_fsm_minus.restype = POINTER(FstStruct)
foma_fsm_parse_regex = foma.fsm_parse_regex
foma_fsm_parse_regex.restype = POINTER(FstStruct)
foma_fsm_read_binary_file = foma.fsm_read_binary_file
foma_fsm_read_binary_file.restype = POINTER(FstStruct)
foma_fsm_sigma_net = foma.fsm_sigma_net
foma_fsm_sigma_net.restype = POINTER(FstStruct)
foma_fsm_topsort = foma.fsm_topsort
foma_fsm_topsort.restype = POINTER(FstStruct)
foma_fsm_union = foma.fsm_union
foma_fsm_union.restype = POINTER(FstStruct)
foma_fsm_upper = foma.fsm_upper
foma_fsm_upper.restype = POINTER(FstStruct)

# Apply functions.
foma_apply_clear = foma.apply_clear
foma_apply_down = foma.apply_down
foma_apply_down.restype = c_char_p
foma_apply_init = foma.apply_init
foma_apply_init.restype = c_void_p
foma_apply_lower_words = foma.apply_lower_words
foma_apply_lower_words.restype = c_char_p
foma_apply_up = foma.apply_up
foma_apply_up.restype = c_char_p
foma_apply_upper_words = foma.apply_upper_words
foma_apply_upper_words.restype = c_char_p
foma_apply_words = foma.apply_words
foma_apply_words.restype = c_char_p

# Set functions.
foma_apply_set_print_space = foma.apply_set_print_space
foma_apply_set_show_flags = foma.apply_set_show_flags
foma_apply_set_space_symbol = foma.apply_set_space_symbol
foma_apply_set_obey_flags = foma.apply_set_obey_flags

# Define functions.
defined_functions_init = foma.defined_functions_init
defined_functions_init.restype = c_void_p
defined_networks_init = foma.defined_networks_init
defined_networks_init.restype = c_void_p
foma_add_defined = foma.add_defined
foma_add_defined.restype = c_int
foma_add_defined_function = foma.add_defined_function
foma_add_defined_function.restype = c_int

# Trie functions.
fsm_trie_add_word = foma.fsm_trie_add_word
fsm_trie_done = foma.fsm_trie_done
fsm_trie_done.restype = POINTER(FstStruct)
fsm_trie_init = foma.fsm_trie_init
fsm_trie_init.restype = c_void_p

# TODO What is this for?
class FstNetworkDefinitions:
    def __init__(self):
        self.defined_handle = defined_networks_init(None)

# TODO What is this for?
class FstFunctionDefinitions:
    def __init__(self):
        self.defined_handle = defined_functions_init(None)
