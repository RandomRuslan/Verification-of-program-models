import ply.yacc as yacc
from lexer import tokens

from classes.expressions import Brace, BinaryExpression, UnaryExpression, IndexOrParameter, Call, Slice
from classes.function import Def, FuncSignature
from classes.source import Source
from classes.statements import NewIdentifier, If, Loop, Break, Block, Expression, Assignment, Statements
from classes.variables import Argument, Array, Identifier, Literal
from node import NodeValue

def set_pos(p, index):
    line_start = p.lexer.lexdata.rfind('\n', 0, p.lexpos(index)) + 1
    return {'line': (p.lineno(index)),
            'pos': (p.lexpos(index) - line_start) + 1}


def add_to_list(l, obj):
    l.extend(obj) if type(obj) == list else l.append(obj)
    return [i for i in l if i is not None]


def p_source(p):
    """source : sourceItems"""
    try:
        p[0] = Source(children=[*p[1]])
    except:
        p[0] = Source()


def p_sourceItems(p):
    """sourceItems :
                   | sourceItem sourceItems"""
    if len(p) == 1:
        p[0] = None
    if len(p) == 3:
        lst = add_to_list([], p[1])
        lst = add_to_list(lst, p[2])
        p[0] = lst or []


def p_sourceItem(p):
    """sourceItem :
                  | funcDef sourceItem"""
    if len(p) == 1:
        p[0] = None
    if len(p) == 3:
        lst = add_to_list([], p[1])
        lst = add_to_list(lst, p[2])
        p[0] = lst or []


def p_funcDef(p):
    """funcDef : DEF funcSignature statements END"""
    stmts = NodeValue(role='statements', children=[*p[3]])
    p[0] = Def(signature=p[2], statements=p[3], pos=set_pos(p, 1), children=[p[2], stmts])


def p_funcSignature(p):
    """funcSignature : identifier LBRACES args RBRACES OF typeRef
                     | identifier LBRACES args RBRACES"""
    identifier = NodeValue(role='identifier', children=[p[1]])
    args = NodeValue(role='args', children=[p[3]])
    if len(p) == 7:
        typeRef = NodeValue(role='typeRef', children=[p[6]])
        p[0] = FuncSignature(name=p[1].name, args=p[3], pos=set_pos(p, 2),
                             func_type=p[7], children=[identifier, args, typeRef])
    else:
        p[0] = FuncSignature(name=p[1].name, args=p[3], pos=set_pos(p, 2), children=[identifier, args])


def p_args(p):
    """args :
            | arg
            | arg COMMA args"""
    if len(p) == 1:
        p[0] = []
    if len(p) == 2:
        p[0] = p[1]
    if len(p) == 4:
        lst = add_to_list([], p[1])
        lst = add_to_list(lst, p[3])
        p[0] = lst or []


def p_arg(p):
    """arg : identifier
           | identifier OF typeRef"""
    identifier = NodeValue(role='identifier', children=[p[1]])
    if len(p) == 4:
        typeRef = NodeValue(role='typeRef', children=[p[3]])
        p[0] = Argument(identifier=p[1], expected_type=p[3], children=[typeRef, identifier])
    else:
        p[0] = Argument(identifier=p[1], children=[identifier])


def p_typeRef(p):
    """typeRef : builtin
               | custom
               | array"""
    p[0] = p[1]


def p_builtin(p):
    """builtin : BUILTIN_BOOL
               | BUILTIN_BYTE
               | BUILTIN_INT
               | BUILTIN_UINT
               | BUILTIN_LONG
               | BUILTIN_ULONG
               | BUILTIN_CHAR
               | BUILTIN_STRING
               | BUILTIN_LIST"""
    p[0] = NodeValue(role=p[1])


def p_custom(p):
    """custom : identifier"""
    p[0] = NodeValue(role=p[1].value)


def p_array(p):
    """array : typeRef ARRAY LBRACKET dec RBRACKET"""
    p[0] = Array(type=p[1], len=p[4][0])


def p_identifiers(p):
    """identifiers : identifier COMMA identifiers
                   | identifier"""
    if len(p) == 2:
        p[0] = p[1]
    if len(p) == 4:
        lst = add_to_list([], p[1])
        lst = add_to_list(lst, p[3])
        p[0] = lst or []


def p_identifier(p):
    """identifier : IDENTIFIER"""
    p[0] = Identifier(name=p[1], type=p.slice[0].type, pos=set_pos(p, 1))


def p_statements(p):
    """statements :
                  | statement statements"""
    if len(p) == 1:
        p[0] = None
    if len(p) == 3:
        lst = add_to_list([], p[1])
        lst = add_to_list(lst, p[2])
        p[0] = lst or []


def p_statement(p):
    """statement : if
                 | loop
                 | repeat
                 | break
                 | expression
                 | block
                 | assignment SEMICOLON"""
    p[0] = p[1]


def p_if(p):
    """if : IF expr THEN statement
          | IF expr THEN statement ELSE statement"""
    _if = NodeValue(role='if', children=[p[2]])
    _then = NodeValue(role='then', children=[p[4]])
    if len(p) == 5:
        p[0] = If(expr=p[2], then_stmt=p[4], pos=set_pos(p, 1), children=[_if, _then])
    else:
        _else = NodeValue(role='else', children=[p[6]])
        p[0] = If(expr=p[2], then_stmt=p[4], else_stmt=p[6], pos=set_pos(p, 1), children=[_if, _then, _else])


def p_loop(p):
    """loop : WHILE expr statements END
            | UNTIL expr statements END"""
    _loop = NodeValue(role=p[1], children=[p[2]])
    _do = NodeValue(role='do', children=[*p[3]])
    p[0] = Loop(expr=p[2], do_stmt=p[3], pos=set_pos(p, 1), children=[_loop, _do])

def p_repeat(p):
    """repeat : statement WHILE expr SEMICOLON
              | statement UNTIL expr SEMICOLON"""
    _loop = NodeValue(role=p[2], children=[p[3]])
    _do = NodeValue(role='do', children=[p[1]])
    p[0] = Loop(expr=p[3], do_stmt=p[1], loop_type=p[2], pos=set_pos(p, 2), children=[_do, _loop])


def p_break(p):
    """break : BREAK SEMICOLON"""
    p[0] = Break(pos=set_pos(p, 1))


def p_expression(p):
    """expression : expr SEMICOLON"""
    expression = NodeValue(role='expression', children=[p[1]])
    p[0] = Expression(expr=p[1], pos=set_pos(p, 2), children=[expression])


def p_block(p):
    """block : BEGIN statements END
             | LFBRACES sourceItems RFBRACES"""
    block = NodeValue(role='block', children=[*p[2]])
    p[0] = Block(statements=p[2], pos=set_pos(p, 1), children=[block])


def p_exprs(p):
    """exprs :
             | expr COMMA exprs"""
    if len(p) == 1:
        p[0] = None
    if len(p) == 4:
        lst = add_to_list([], p[1])
        lst = add_to_list(lst, p[3])
        p[0] = lst or []


def p_expr(p):
    """expr : binary
            | unary
            | braces
            | call
            | slice
            | place
            | literal"""
    p[0] = p[1]


def p_assignment(p):
    """assignment : identifiers ASSIGNMENT expr"""
    identifiers = NodeValue(role='identifiers', children=[NodeValue(role=str(p[1]))])
    value = NodeValue(role='value', children=[p[3]])
    assignment = NodeValue(role='assignment', children=[identifiers, value])
    p[0] = Assignment(p[1], p[3], pos=set_pos(p, 2), children=[assignment])


def p_binary(p):
    """binary : expr PLUS expr
              | expr MINUS expr
              | expr DIVIDE expr
              | expr MUL expr
              | expr LESS_EQ expr
              | expr MORE_EQ expr
              | expr MORE expr
              | expr NOT_EQ expr
              | expr EQUAL expr
              | expr AND expr
              | expr OR expr"""
    binary = NodeValue(role=p[2], children=[p[1], p[3]])
    p[0] = BinaryExpression(left=p[1], right=p[3], operand=p[2], children=[binary])


def p_unary(p):
    """unary : NOT expr
             | MINUS expr"""
    unary = NodeValue(role=p[1], children=[p[2]])
    p[0] = UnaryExpression(expr=p[2], operand=p[1], children=[unary])


def p_braces(p):
    """braces : LBRACES expr RBRACES"""
    braces = NodeValue(role='braces', children=[p[2]])
    p[0] = Brace(expr=p[2], pos=set_pos(p, 1), brace=True, children=[braces])


def p_call(p):
    """call : expr LBRACES exprs RBRACES"""
    parameters = []
    for i, parameter in enumerate(p[3]):
        parameters.append(IndexOrParameter(exprs=parameter, index=i, pos=set_pos(p, 1), children=p[3]))
    call = NodeValue('call', children=[parameters])
    expr = NodeValue('expr', children=[p[1]])
    p[0] = Call(expr=p[3], parameters=parameters, pos=set_pos(p, 2), children=[expr, call])


def p_slice(p):
    """slice : expr LBRACKET ranges RBRACKET"""
    indexes = []
    ind = p[3] if type(p[3]) == list else [p[3]]
    for i, index in enumerate(ind):
        indexes.append(IndexOrParameter(exprs=index, index=i, pos=set_pos(p, 1), children=p[3]))
    expr = NodeValue('expr', children=[p[1]])
    p[0] = Slice(expr=p[1], indexes=indexes, pos=set_pos(p, 2), children=[expr, *ind])


def p_ranges(p):
    """ranges : expr
              | expr TWODOTS expr"""
    if len(p) == 2:
        p[0] = p[1]
    if len(p) == 4:
        lst = add_to_list([], p[1])
        lst = add_to_list(lst, p[3])
        p[0] = lst or []


def p_place(p):
    """place : identifier"""
    p[0] = p[1]


def p_literal(p):
    """literal : bool
               | str
               | char
               | hex
               | bits
               | dec"""
    type = NodeValue(role='type', children=[NodeValue(role=p[1][0])])
    value = NodeValue(role='value',children=[NodeValue(role=p[1][1])])
    literal = NodeValue(role='literal', children=[type, value])
    p[0] = Literal(value=p[1][0], type=p[1][1], pos=set_pos(p, 1), children=[literal])


def p_str(p):
    """str : STR"""
    p[0] = p[1], p.slice[0].type


def p_char(p):
    """char : CHAR"""
    p[0] = p[1], p.slice[0].type


def p_hex(p):
    """hex : HEX"""
    p[0] = p[1], p.slice[0].type


def p_bits(p):
    """bits : BITS"""
    p[0] = p[1], p.slice[0].type


def p_dec(p):
    """dec : DEC"""
    p[0] = p[1], p.slice[0].type


def p_bool(p):
    """bool : BOOL"""
    p[0] = p[1], p.slice[0].type


def p_error(p):
    print('Unexpected token:', p)


parser = yacc.yacc(debug=True)


def parse_tokens(path):
    with open(path) as file_handler:
        input_file = file_handler.read()
        root = parser.parse(input_file)
        root.source_name = path
    return root
