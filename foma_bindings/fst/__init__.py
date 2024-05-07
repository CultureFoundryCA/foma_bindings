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

from foma_bindings import *
from sys import maxsize
from ctypes import c_bool
import re
import warnings

# This regex matches all foma flag diacritics.
# https://giellalt.uit.no/lang/sme/docu-sme-flag-diacritics.html
# Flag diacritic example: @P.Name.Value@
# Valid flag operators: P, R, D, U, C, N.
# Value part is optional.
MATCH_NAME = 'full_flag'
FLAGS_REGEX = re.compile(f'(?P<{MATCH_NAME}>@[PRDUCN][.][^@.\s]+([.][^@.\s]+)?@)')

class Fst:
    '''
    This class loads a compiled foma binary into memory, and allows operations on it.

    Here is an example of use:

    ```python
    from foma_bindings import Fst
    fst = Fst.load('/path/to/foma/binary')
    fst.apply_up('fox', flags=Fst.PRINT_FLAGS | Fst.PRINT_SPACES)
    ```

    Constants for printing:
        - PRINT_SPACES
        - PRINT_FLAGS
        - DONT_OBEY_FLAGS
        - TOKENIZE
        - VERBOSE = TOKENIZE | PRINT_FLAGS

    Word-Accessor Functions:
        - apply_down
        - apply_up
        - lower_words
        - upper_words
        - words

    FST Functions:
        - get_alphabet
        - get_flag_diacritics
        - union
        - intersect
        - minus
        - concatenate
        - compose
        - lower
        - upper
        - flatten
    '''    

    _network_definitions = FstNetworkDefinitions()
    _function_definitions = FstFunctionDefinitions()

    # This is the symbol to split a word on tokens, i.e. "fox+V" becomes ['f','o','x','+V'].
    _TOKENIZE_SYMBOL = b'\x07'

    # Bit flags for different options when printing output.
    # TODO PRINT_SPACES and TOKENIZE do not mesh well together. What to do?
    NO_FLAGS = 0
    SHOW_SPACES = 1
    PRINT_SPACES = SHOW_SPACES
    SHOW_FLAGS = 2
    PRINT_FLAGS = SHOW_FLAGS
    DONT_OBEY_FLAGS = 4
    TOKENIZE = 8
    VERBOSE = TOKENIZE | PRINT_FLAGS

    #region Class and Static Methods
    @classmethod
    def define(cls, definition, name):
        '''Defines an FSM constant; can be supplied regex or existing FSM.
        This link explains the Xerox regex formalism:
        https://github.com/CultureFoundryCA/foma/blob/master/foma/docs/simpleintro.md'''
        # TODO needs a docstring, it's not clear what it means by "defines an FSM constant".
        name = cls.encode(name)
        if isinstance(definition, Fst):
            _ = foma.add_defined(c_void_p(cls._network_definitions.defined_handle), foma_fsm_copy(definition.fst_handle), c_char_p(name))
        elif isinstance(definition, str):
            regex = cls.encode(definition)
            _ = foma.add_defined(c_void_p(cls._network_definitions.defined_handle), foma_fsm_parse_regex(c_char_p(regex), c_void_p(cls._network_definitions.defined_handle), c_void_p(cls._function_definitions.defined_handle)), c_char_p(name))
        else:
            raise ValueError("Expected str, unicode, or FSM")

    @classmethod
    def define_function(cls, prototype, definition):
        """Defines an FSM function."""
        # Prototype is a 2-tuple (name, (arg1name, ..., argname))
        # Definition is regex using prototype variables
        # TODO needs a docstring or needs a better docstring.
        name = cls.encode(prototype[0] + '(')
        if isinstance(definition, str):
            numargs = len(prototype[1])
            for i in range(numargs):
                definition = definition.replace(prototype[1][i], "@ARGUMENT0%i@" % (i+1))
            regex = cls.encode(definition + ';')
            # TODO check this retval
            retval = foma.add_defined_function(c_void_p(cls._function_definitions.deffhandle), c_char_p(name), c_char_p(regex), c_int(numargs))
        else:
            raise ValueError("Expected regex as definition")
        
    @classmethod
    def wordlist(cls, wordlist, minimize=True):
        """Create FSM directly from wordlist.
           Returns a trie-shaped deterministic automaton if not minimized."""
        
        # TODO Fix this naming.
        th = fsm_trie_init()
        for w in wordlist:
            thisword = cls.encode(w)
            fsm_trie_add_word(c_void_p(th), c_char_p(thisword))
        fsm = cls()
        fsm.fst_handle = fsm_trie_done(c_void_p(th))
        if minimize:
            fsm.fst_handle = foma_fsm_minimize(fsm.fst_handle)
        return fsm

    @classmethod
    def load(cls, filename):
        """Load binary FSM from file."""
        fsm = cls()
        fsm.fst_handle = foma_fsm_read_binary_file(c_char_p(Fst.encode(filename)))
        if not fsm.fst_handle:
            raise ValueError("File error.")
        return fsm

    @staticmethod
    def encode(string):
        # TODO clean up this commenting
        # TODO make private
        # type: (Any) -> bytes
        """Makes sure str and unicode are converted."""
        if isinstance(string, str):
            return string.encode('utf8')
        elif isinstance(string, bytes):
            return string
        else:
            return Fst.encode(str(string))

    @staticmethod
    def decode(text):
        # TODO make private
        # TODO needs a docstring or needs a better docstring.
        if text is None:
            return None
        elif isinstance(text, bytes):
            # Assume output is UTF-8 encoded:
            return text.decode('UTF-8')
        else:
            assert isinstance(text, str)
            return text

    #endregion

    #region Private Functions
    def _get_applyer_handle(self, flags):
        '''Initializes a handle to do apply-type functions on. Also sets the output flags on that handle. Flags do not persist once handle is destroyed.'''
        applyer_handle = foma_apply_init(self.fst_handle)

        # Handle the flags to the function.
        if flags & Fst.TOKENIZE:
            foma_apply_set_space_symbol(c_void_p(applyer_handle), c_char_p(Fst._TOKENIZE_SYMBOL))

        if flags & Fst.PRINT_FLAGS:
            foma_apply_set_show_flags(c_void_p(applyer_handle), c_bool(True))

        if flags & Fst.PRINT_SPACES:
            foma_apply_set_print_space(c_void_p(applyer_handle), c_bool(True))

        if flags & Fst.DONT_OBEY_FLAGS:
            foma_apply_set_obey_flags(c_void_p(applyer_handle),  c_bool(False))
        
        return applyer_handle

    def _apply(self, apply_strategy, word=None, flags=NO_FLAGS):
        '''Takes an application function and executes it on the FST.'''
        if not self.fst_handle:
            raise ValueError('FST not defined')

        applyer_handle = self._get_applyer_handle(flags)

        # TODO why is word set here and not in the while? Can this be cleaned up by always passing the word?
        # Call the apply_function with appropriate word argument.
        if word:
            output = apply_strategy(c_void_p(applyer_handle), c_char_p(self.encode(word)))
        else:
            output = apply_strategy(c_void_p(applyer_handle))

        # Yield results until all FST output for the given input is consumed.
        while True:
            if output is None:
                foma_apply_clear(c_void_p(applyer_handle))
                return
            else:
                if flags & Fst.TOKENIZE:
                    yield [Fst.decode(token) for token in output[:-1].split(Fst._TOKENIZE_SYMBOL)]
                else:
                    yield self.decode(output)

            if word:
                output = apply_strategy(c_void_p(applyer_handle), None)
            else:
                output = apply_strategy(c_void_p(applyer_handle))


    # Functions to call functions through C API.
    def _foma_call_unary(self, unary_func, minimize=True):
        '''Calls a supplied unary function on the FST.'''
        if self.fst_handle:
            handle = unary_func(foma_fsm_copy(self.fst_handle))
            if minimize:
                handle = foma_fsm_minimize(handle)
            return handle
        else:
            raise ValueError('Undefined FST')
        
    def _foma_call_binary(self, other, binary_func, minimize=True):
        '''Calls a supplied binary function on the FST and a provided FST.'''
        if self.fst_handle and other.fst_handle:
            handle = binary_func(foma_fsm_copy(self.fst_handle), foma_fsm_copy(other.fst_handle))
            if minimize:
                handle = foma_fsm_minimize(handle)
            return handle
        else:
            raise ValueError('Undefined FST')

    #endregion

    #region Public Functions
    # Word accessor functions.
    def apply_down(self, word, flags=NO_FLAGS):
        '''Apply a word down the FST. Example: fox+N+Pl -> foxes.'''
        return self._apply(foma_apply_down, word, flags)

    def apply_up(self, word, flags=NO_FLAGS):
        '''Apply a word up the FST. Example: foxes -> fox+N+Pl.'''
        return self._apply(foma_apply_up, word, flags)

    def lower_words(self, flags=NO_FLAGS):
        return self._apply(foma_apply_lower_words, flags=flags)

    def upper_words(self, flags=NO_FLAGS):
        return self._apply(foma_apply_upper_words, flags=flags)

    def words(self, flags=NO_FLAGS):
        return self._apply(foma_apply_words, flags=flags)
        
    # FST operations.
    def get_alphabet(self, minimize=True, flags=SHOW_FLAGS | DONT_OBEY_FLAGS):
        '''Gets the alphabet of the FST.'''
        sigma = Fst()
        sigma.fst_handle = self._foma_call_unary(foma_fsm_sigma_net, minimize)
        return sigma.words(flags)
    
    # Alias to get_alphabet since both are very different yet valid names for the same function.
    get_sigma = get_alphabet

    def get_flag_diacritics(self, minimize=True):
        '''Returns a list of all the flag diacritics in the FST.'''
        alphabet = ' '.join(self.get_alphabet(minimize, flags=Fst.SHOW_FLAGS | Fst.DONT_OBEY_FLAGS))
        flag_diacritics = [match.groupdict()[MATCH_NAME] for match in FLAGS_REGEX.finditer(alphabet)]
        return flag_diacritics

    def union(self, other, minimize=True):
        '''Returns the union of two FSTs.'''
        fst = Fst()
        fst.fst_handle = self._foma_call_binary(other, foma_fsm_union, minimize)
        return fst

    def intersect(self, other, minimize=True):
        '''Returns the intersection of two FSTs.'''
        fst = Fst()
        fst.fst_handle = self._foma_call_binary(other, foma_fsm_intersect, minimize)
        return fst

    def minus(self, other, minimize=True):
        '''Returns the difference of two FSTs.'''
        fst = Fst()
        fst.fst_handle = self._foma_call_binary(other, foma_fsm_minus, minimize)
        return fst

    def concatenate(self, other, minimize=True):
        '''Returns the concatenation of two FSTs.'''
        fst = Fst()
        fst.fst_handle = self._foma_call_binary(other, foma_fsm_concat, minimize)
        return fst

    def compose(self, other, minimize=True):
        '''Returns the composition of two FSTs.'''
        fst = Fst()
        fst.fst_handle = self._foma_call_binary(other, foma_fsm_compose, minimize)
        return fst
    
    def lower(self, minimize=True):
        fst = Fst()
        fst.fst_handle = self._foma_call_unary(foma_fsm_lower, minimize)
        return fst

    def upper(self, minimize=True):
        fst = Fst()
        fst.fst_handle = self._foma_call_unary(foma_fsm_upper, minimize)
        return fst

    def flatten(self):
        fst = Fst()
        epsilon_fst = Fst(EPSILON_SYMBOL)
        fst.fst_handle = foma_fsm_flatten(foma_fsm_copy(self.fst_handle), foma_fsm_copy(epsilon_fst.fst_handle))
        return fst 
    
    #endregion

    #region Dunders
    def __init__(self, regex=False):
        if regex:
            self.regex = self.encode(regex)
            self.fst_handle = foma_fsm_parse_regex(c_char_p(self.regex), c_void_p(self._network_definitions.defined_handle), c_void_p(self._function_definitions.defined_handle))
            if not self.fst_handle:
                raise ValueError("Syntax error in regex")
        else:
            self.fst_handle = None
        self.get_item_applyer = None

    def __getitem__(self, key):
        if not self.fst_handle:
            raise KeyError('FST not defined')
        if not self.get_item_applyer:
            self.get_item_applyer = foma_apply_init(self.fst_handle)
        result = []
        output = foma_apply_down(c_void_p(self.get_item_applyer), c_char_p(self.encode(key)))
        while True:
            if output is None:
                return result
            else:
                result.append(output)
                output = foma_apply_down(c_void_p(self.get_item_applyer), None)
            
    def __del__(self):
        if self.fst_handle:
            foma_fsm_destroy(self.fst_handle)

    def __str__(self):
        if not self.fst_handle:
            raise ValueError('FSM not defined')
        foma_fsm_count(self.fst_handle)

        return f'Name: {self.fst_handle.contents.name}\n\
                States: {self.fst_handle.contents.statecount}\n\
                Transitions: {self.fst_handle.contents.arccount}\n\
                Final States: {self.fst_handle.contents.finalcount}\n\
                Deterministic: {self.fst_handle.contents.is_deterministic}\n\
                Minimized: {self.fst_handle.contents.is_minimized}\n\
                Arity: {self.fst_handle.contents.arity}\n'

    def __len__(self):
        CYCLIC = -1
        OVERFLOW = -2
        UNKNOWN = -3

        if self.fst_handle:
            if self.fst_handle.contents.pathcount == UNKNOWN:
                self.fst_handle = foma_fsm_topsort(self.fst_handle)
            if self.fst_handle.contents.pathcount == CYCLIC:
                raise ValueError("FSM is cyclic")
            if self.fst_handle.contents.pathcount == OVERFLOW:
                return maxsize
            return self.fst_handle.contents.pathcount
        else:
            raise ValueError("FSM not defined")
        
    def __add__(self, other):
        return self.concat(other)

    def __sub__(self, other):
        return self.minus(other)
    
    def __le__(self, other):
        if self.fst_handle and other.fst_handle:
            return bool(c_int(foma_fsm_isempty(foma_fsm_minimize(foma_fsm_minus(foma_fsm_copy(self.fst_handle),foma_fsm_copy(other.fst_handle))))))
        else:
            raise ValueError('Undefined FST')

    def __lt__(self, other):
        if self.fst_handle and other.fst_handle:
            return (not self.__eq__(other)) and bool(c_int(foma_fsm_isempty(foma_fsm_minimize(foma_fsm_minus(foma_fsm_copy(self.fst_handle),foma_fsm_copy(other.fst_handle))))))
        else:
            raise ValueError('Undefined FST')        
        
    def __or__(self, other):
        return self.union(other)

    def __and__(self, other):
        return self.intersect(other)

    def __eq__(self, other):
        if self.fst_handle and other.fst_handle:
            return bool(c_int(foma_fsm_equivalent(foma_fsm_copy(self.fst_handle), foma_fsm_copy(other.fst_handle))))
        else:
            raise ValueError('Undefined FST')
    
    def __ne__(self, other):
        return not(self.__eq__(other))

    def __contains__(self, word):
        # TODO fix this variable name
        af = self.apply_down(word)
        try:
            # TODO fix this variable name
            i = af.next()
            return True
        except StopIteration:
            return False
                
    def __call__(self, other):
        if isinstance(other, str):
            return Fst("{" + other + "}").compose(self)
        else:
            return other.compose(self)
    
    def __invert__(self):
        fst = Fst()
        fst.fst_handle = self._foma_call_unary(foma_fsm_complement)
        return fst

    def __iter__(self):
        return self._apply(foma_apply_upper_words, word=None, flags=Fst.NO_FLAGS)
    
    #endregion
    
    #region String Matching
    
    def query_with_head_tags(self, stem: str, head_tags: dict[str,list[str]], tail_tags: dict[str,list[str]], debug: bool = False) -> zip:
        '''The head- and tail-tags should be the feature names and feature values, i.e. {polarity: [POS, NEG], subject: None}. This list must be appropriately ordered and exhaustive.'''

        # We'll use this expression to freely insert flag diacritics into the query.
        flag_diacritics = " | ".join([f'"{flag}"' for flag in self.get_flag_diacritics()])
        
        # Build the query to send to foma.
        query_builder = ''

        # Loop over tags and create the head of the query..
        for tags in head_tags.values():
            if tags is None:
                query_builder += '[ ? ]'
            else:
                tagging_options = [f'"{tag}+"' if tag != '0' else '0' for tag in tags]
                query_builder += f"[ {' | '.join(tagging_options)} ]"

        # Insert stem into query.
        query_builder += '{%s}' % stem

        # Loop over tags and create the tail of the query.
        for tags in tail_tags.values():
            if tags is None:
                query_builder += '[ ? ]'
            else:
                tagging_options = [f'"+{tag}"' if tag != '0' else '0' for tag in tags]
                query_builder += f"[ {' | '.join(tagging_options)} ]"

        query = f'[ {query_builder} ]'

        # Freely insert flag diacritics into the query. Needed for composition.
        query += ' / [ "0" ]' if len(flag_diacritics) == 0 else f' / [ {flag_diacritics} ]'

        if debug:
            print(f'Query: {query}')

        selector_fst = Fst(query)

        # Apply query to fst and return generator of the analyses.
        resulting_fst = selector_fst.compose(self)
        return resulting_fst.upper_words(), resulting_fst.lower_words()

    def query(self, stem:str, debug = False, **kwargs) -> zip:
        '''kwargs should be the feature names and feature values, i.e. {polarity: [POS, NEG], subject: None}. This list must be appropriately ordered and exhaustive.'''

        warnings.warn("The `query` function will be deprecated in 2 months; please use `query_with_head_tags` instead.")

        # We'll use this expression to freely insert flag diacritics into the query.
        flag_diacritics = " | ".join([f'"{flag}"' for flag in self.get_flag_diacritics()])

        # Build query.
        query_builder = '{%s}' % stem

        # Loop over tags and create the query.
        for tags in kwargs.values():
            if tags is None:
                query_builder += '[ ? ]'
            else:
                tagging_options = [f'"+{tag}"' for tag in tags]
                query_builder += f"[ {' | '.join(tagging_options)} ]"

        query = f'[ {query_builder} ]'

        # Freely insert flag diacritics into the query. Needed for composition.
        if flag_diacritics is not None:
            query += f' / [ {flag_diacritics} ]'

        if debug:
            print(f'Query: {query}')

        selector_fst = Fst(query)

        # Apply query to fst and return generator of the analyses.
        resulting_fst = selector_fst.compose(self)
        return resulting_fst.upper_words(), resulting_fst.lower_words()

    #endregion
