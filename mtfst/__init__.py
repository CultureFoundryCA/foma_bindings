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

# from foma-bindings.fst import Fst
# from foma-bindings import *

# Untested and unclean.
# class MTFSM(Fst):
#     '''Multi-Tape Finite State Machine'''

#     EPSILON_FST = Fst(EPSILON_SYMBOL)

#     def __init__(self, regex=False, num_tapes=2):
#         if isinstance(regex, str):
#             Fst.__init__(self, regex)
#             self.fst_handle = foma_fsm_flatten(foma_fsm_copy(self.fst_handle), foma_fsm_copy(MTFSM.EPSILON_FST.fst_handle))
#             self.num_tapes = num_tapes
#         elif isinstance(regex, Fst):
#             self.fst_handle = foma_fsm_copy(regex.fst_handle)
#             self.regex = None
#             self.num_tapes = num_tapes
#         else:
#             self.fst_handle = None
#             self.regex = None
        
#     def __str__(self):
#         if not self.fst_handle:
#             raise ValueError('FSM not defined')

#         foma_fsm_count(self.fst_handle)
        
#         return f'Name: {self.fst_handle.contents.name}\n\
#                 States: {self.fst_handle.contents.statecount}\n\
#                 Transitions: {self.fst_handle.contents.arccount}\n\
#                 Final States: {self.fst_handle.contents.finalcount}\n\
#                 Deterministic: {self.fst_handle.contents.is_deterministic}\n\
#                 Minimized: {self.fst_handle.contents.is_minimized}\n\
#                 Number of Tapes: {self.num_tapes}'
    
#     def generate(self, word):
#         # TODO variable naming
#         m = self.num_tapes
#         regx = '[{' + word + '}/' + EPSILON_SYMBOL + ' .o. [? 0:?^' + str(m-1) + ']*].l'
#         reg = Fst(regx)
#         gr = Fst()
#         gr.fst_handle = foma_fsm_copy(self.fst_handle)
#         res = MTFSM(reg.intersect(gr), num_tapes = m)
#         return res
    
#     def parse(self, word):
#         # TODO variable naming
#         #[word/□ .o. [0:?^(num_tapes-1) ?]*].l & Grammar ;
#         m = self.num_tapes
#         regx = (u'[{' + word + u'}/□ .o. [0:?^' + str(m-1) + u' ?]*].l')
#         reg = Fst(regx)
#         gr = Fst()
#         gr.fst_handle = foma_fsm_copy(self.fst_handle)
#         res = MTFSM(reg.intersect(gr), num_tapes = m)        
#         return res
    
#     def join(self, other):
#         """Joins two multitape FSMs by composition. E.g.
#             [ a d ]     [ c □ □ ]                  [ a d □ ]
#         A = [ b e ] B = [ d f g ], and A.join(B) = [ b e □ ]
#             [ c □ ]     [ e f g ]                  [ c □ □ ]
#                                                    [ d f g ]
#                                                    [ e f g ] """

#         m = self.num_tapes        
#         n = other.num_tapes
#         pada = Fst('[0:□^' + str(m) +' [0:?^' + str(n-1) + ' - 0:□^' + str(n-1) + '] | ?^' + str(m) + ' 0:?^' + str(n-1) + ']*')
#         padb = Fst('[[0:?^' + str(m-1) + ' - 0:□^' + str(m-1) + ' ] 0:□^' + str(n) + '| 0:?^' + str(m-1) + ' ?^' + str(n) + ']*')
#         extenda = self.compose(pada).lower()
#         extendb = other.compose(padb).lower()
#         flt = Fst('~[?^' + str(m+n-1) +'* [□^' + str(m) + ' ?^' + str(n-1) + ' [?^' + str(m-1) + ' □^' + str(n) + ' |[?^' + str(m-1) +' - □^' + str(m-1) + ' ] □ [?^' + str(n-1) + ' - □^' + str(n-1) + ' ]] | ?^' + str(m-1) + ' □^' + str(n) + ' [□^' + str(m) + ' ?^' + str(n-1) + ' |[?^' + str(m-1) + ' - □^' + str(m-1) + ' ] □ [?^' + str(n-1) + ' - □^' + str(n-1) + ' ]]] ?*]')
#         res = extenda & extendb & flt
#         result = MTFSM(res, m + n - 1)
#         return result

#     def _apply(self, apply_strategy, word=None):
#         if not self.fst_handle:
#             raise ValueError('FST not defined')
#         applyer_handle = foma_apply_init(self.fst_handle)
#         output = apply_strategy(c_void_p(applyer_handle))
#         while True:
#             if output is None:
#                 foma_apply_clear(c_void_p(applyer_handle))
#                 return
#             else:
#                 yield output
#             if word:
#                 output = apply_strategy(c_void_p(applyer_handle), None)
#             else:
#                 output = apply_strategy(c_void_p(applyer_handle))

#     def __iter__(self):
#         return self._mtwords()

#     def __add__(self, other):
#         return self.join(other)

#     def _fmt(self, word):
#         cols = word
#         colchunks = [map(lambda z: len(z), word[x:x+self.num_tapes]) for x in range(0, len(word), self.num_tapes)]
#         col_widths = [max(x) for x in colchunks]
#         format = '  '.join(['%%-%ds' % width for width in col_widths])
#         # string to rows
#         rows = [[word[y] for y in range(x, len(word), self.num_tapes)] for x in range(self.num_tapes)]
#         s = ''
#         for row in rows:
#             #s += format % tuple(row) + '\n'
#             s += ''.join(row) + '\n'
#         return s

#     def _mtwords(self):
#         apply_strategy = foma_apply_upper_words
#         if not self.fst_handle:
#             raise ValueError('FST not defined')
#         applyer_handle = foma_apply_init(self.fst_handle)
#         toksym = '\x07'
#         foma_apply_set_space_symbol(c_void_p(applyer_handle), c_char_p(self.encode(toksym)))
#         output = apply_strategy(c_void_p(applyer_handle))
#         while True:
#             if output is None:
#                 foma_apply_clear(c_void_p(applyer_handle))
#                 return
#             else:
#                 yield self._fmt(self.decode(output)[:-1].split('\x07'))
#             output = apply_strategy(c_void_p(applyer_handle))
