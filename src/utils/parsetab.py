
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'leftEQUALSNOT_EQUALSLESSGREATERLESS_EQUALSGREATER_EQUALSleftORleftXORleftANDleftPLUSMINUSleftTIMESDIVIDEINT_DIVMODULOleftEXPrightUMINUSUNOTAND DIVIDE EQUALS EXP FLOAT GREATER GREATER_EQUALS INTEGER INT_DIV LESS LESS_EQUALS LPAREN MINUS MODULO NAME NOT NOT_EQUALS OR PLUS RPAREN TIMES XORexpression : LPAREN expression RPARENexpression : NAME LPAREN expression RPARENstatement : expression\n        expression : expression PLUS expression\n                  | expression MINUS expression\n                  | expression TIMES expression\n                  | expression DIVIDE expression\n                  | expression INT_DIV expression\n                  | expression EXP expression\n                  | expression MODULO expression\n                  | expression EQUALS expression\n                  | expression NOT_EQUALS expression\n                  | expression LESS expression\n                  | expression GREATER expression\n                  | expression LESS_EQUALS expression\n                  | expression GREATER_EQUALS expression\n                  | expression AND expression\n                  | expression XOR expression\n                  | expression OR expression\n        expression : MINUS expression %prec UMINUSexpression : NOT expression %prec UNOTexpression : FLOAT\n                     | INTEGER\n        expression : NAME'
    
_lr_action_items = {'LPAREN':([0,2,3,4,5,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,25,],[2,2,25,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,]),'NAME':([0,2,4,5,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,25,],[3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,]),'MINUS':([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,],[4,9,4,-24,4,4,-22,-23,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,9,4,-20,-21,-4,-5,-6,-7,-8,-9,-10,9,9,9,9,9,9,9,9,9,-1,9,-2,]),'NOT':([0,2,4,5,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,25,],[5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,]),'FLOAT':([0,2,4,5,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,25,],[6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,]),'INTEGER':([0,2,4,5,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,25,],[7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,]),'$end':([1,3,6,7,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,46,],[0,-24,-22,-23,-20,-21,-4,-5,-6,-7,-8,-9,-10,-11,-12,-13,-14,-15,-16,-17,-18,-19,-1,-2,]),'PLUS':([1,3,6,7,24,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,],[8,-24,-22,-23,8,-20,-21,-4,-5,-6,-7,-8,-9,-10,8,8,8,8,8,8,8,8,8,-1,8,-2,]),'TIMES':([1,3,6,7,24,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,],[10,-24,-22,-23,10,-20,-21,10,10,-6,-7,-8,-9,-10,10,10,10,10,10,10,10,10,10,-1,10,-2,]),'DIVIDE':([1,3,6,7,24,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,],[11,-24,-22,-23,11,-20,-21,11,11,-6,-7,-8,-9,-10,11,11,11,11,11,11,11,11,11,-1,11,-2,]),'INT_DIV':([1,3,6,7,24,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,],[12,-24,-22,-23,12,-20,-21,12,12,-6,-7,-8,-9,-10,12,12,12,12,12,12,12,12,12,-1,12,-2,]),'EXP':([1,3,6,7,24,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,],[13,-24,-22,-23,13,-20,-21,13,13,13,13,13,-9,13,13,13,13,13,13,13,13,13,13,-1,13,-2,]),'MODULO':([1,3,6,7,24,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,],[14,-24,-22,-23,14,-20,-21,14,14,-6,-7,-8,-9,-10,14,14,14,14,14,14,14,14,14,-1,14,-2,]),'EQUALS':([1,3,6,7,24,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,],[15,-24,-22,-23,15,-20,-21,-4,-5,-6,-7,-8,-9,-10,-11,-12,-13,-14,-15,-16,-17,-18,-19,-1,15,-2,]),'NOT_EQUALS':([1,3,6,7,24,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,],[16,-24,-22,-23,16,-20,-21,-4,-5,-6,-7,-8,-9,-10,-11,-12,-13,-14,-15,-16,-17,-18,-19,-1,16,-2,]),'LESS':([1,3,6,7,24,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,],[17,-24,-22,-23,17,-20,-21,-4,-5,-6,-7,-8,-9,-10,-11,-12,-13,-14,-15,-16,-17,-18,-19,-1,17,-2,]),'GREATER':([1,3,6,7,24,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,],[18,-24,-22,-23,18,-20,-21,-4,-5,-6,-7,-8,-9,-10,-11,-12,-13,-14,-15,-16,-17,-18,-19,-1,18,-2,]),'LESS_EQUALS':([1,3,6,7,24,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,],[19,-24,-22,-23,19,-20,-21,-4,-5,-6,-7,-8,-9,-10,-11,-12,-13,-14,-15,-16,-17,-18,-19,-1,19,-2,]),'GREATER_EQUALS':([1,3,6,7,24,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,],[20,-24,-22,-23,20,-20,-21,-4,-5,-6,-7,-8,-9,-10,-11,-12,-13,-14,-15,-16,-17,-18,-19,-1,20,-2,]),'AND':([1,3,6,7,24,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,],[21,-24,-22,-23,21,-20,-21,-4,-5,-6,-7,-8,-9,-10,21,21,21,21,21,21,-17,21,21,-1,21,-2,]),'XOR':([1,3,6,7,24,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,],[22,-24,-22,-23,22,-20,-21,-4,-5,-6,-7,-8,-9,-10,22,22,22,22,22,22,-17,-18,22,-1,22,-2,]),'OR':([1,3,6,7,24,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,],[23,-24,-22,-23,23,-20,-21,-4,-5,-6,-7,-8,-9,-10,23,23,23,23,23,23,-17,-18,-19,-1,23,-2,]),'RPAREN':([3,6,7,24,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,],[-24,-22,-23,44,-20,-21,-4,-5,-6,-7,-8,-9,-10,-11,-12,-13,-14,-15,-16,-17,-18,-19,-1,46,-2,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'expression':([0,2,4,5,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,25,],[1,24,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,45,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> expression","S'",1,None,None,None),
  ('expression -> LPAREN expression RPAREN','expression',3,'p_expression_group','parser.py',145),
  ('expression -> NAME LPAREN expression RPAREN','expression',4,'p_expression_func','parser.py',149),
  ('statement -> expression','statement',1,'p_statement_expr','parser.py',161),
  ('expression -> expression PLUS expression','expression',3,'p_expression_binop','parser.py',166),
  ('expression -> expression MINUS expression','expression',3,'p_expression_binop','parser.py',167),
  ('expression -> expression TIMES expression','expression',3,'p_expression_binop','parser.py',168),
  ('expression -> expression DIVIDE expression','expression',3,'p_expression_binop','parser.py',169),
  ('expression -> expression INT_DIV expression','expression',3,'p_expression_binop','parser.py',170),
  ('expression -> expression EXP expression','expression',3,'p_expression_binop','parser.py',171),
  ('expression -> expression MODULO expression','expression',3,'p_expression_binop','parser.py',172),
  ('expression -> expression EQUALS expression','expression',3,'p_expression_binop','parser.py',173),
  ('expression -> expression NOT_EQUALS expression','expression',3,'p_expression_binop','parser.py',174),
  ('expression -> expression LESS expression','expression',3,'p_expression_binop','parser.py',175),
  ('expression -> expression GREATER expression','expression',3,'p_expression_binop','parser.py',176),
  ('expression -> expression LESS_EQUALS expression','expression',3,'p_expression_binop','parser.py',177),
  ('expression -> expression GREATER_EQUALS expression','expression',3,'p_expression_binop','parser.py',178),
  ('expression -> expression AND expression','expression',3,'p_expression_binop','parser.py',179),
  ('expression -> expression XOR expression','expression',3,'p_expression_binop','parser.py',180),
  ('expression -> expression OR expression','expression',3,'p_expression_binop','parser.py',181),
  ('expression -> MINUS expression','expression',2,'p_expression_uminus','parser.py',217),
  ('expression -> NOT expression','expression',2,'p_expression_unot','parser.py',221),
  ('expression -> FLOAT','expression',1,'p_expression_number','parser.py',225),
  ('expression -> INTEGER','expression',1,'p_expression_number','parser.py',226),
  ('expression -> NAME','expression',1,'p_expression_name','parser.py',231),
]