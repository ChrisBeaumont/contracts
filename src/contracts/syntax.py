from numbers import Number
# All the imports from pyparsing go here
#from contracts import use_pyparsing
if False: # pragma: no cover
    print('contracts: Warning: using my private version of PyParsing for testing.')
    from .mypyparsing import (delimitedList, Forward, Literal, stringEnd, nums, Word, #@UnusedImport
        CaselessLiteral, Combine, Optional, Suppress, OneOrMore, ZeroOrMore, opAssoc, #@UnusedImport
        operatorPrecedence, oneOf, ParseException, ParserElement, alphas, alphanums, #@UnusedImport
        ParseFatalException, FollowedBy, NotAny, Or, MatchFirst, Keyword, Group, White, lineno, col) #@UnusedImport
else:
    from pyparsing import (delimitedList, Forward, Literal, stringEnd, nums, Word, #@UnusedImport
        CaselessLiteral, Combine, Optional, Suppress, OneOrMore, ZeroOrMore, opAssoc, #@UnusedImport
        operatorPrecedence, oneOf, ParseException, ParserElement, alphas, alphanums, #@UnusedImport
        ParseFatalException, FollowedBy, NotAny, Or, MatchFirst, Keyword, Group, White, lineno, col) #@UnusedImport
    
from contracts.pyparsing_utils import myOperatorPrecedence

# Enable memoization (much faster!)
ParserElement.enablePackrat()

from .interface import Where

class ParsingTmp: 
    # TODO: FIXME: decide on an order, if we do the opposite it doesn't work.
    contract_types = []
    rvalues_types = []
    keywords = []

def add_contract(x):
    ParsingTmp.contract_types.append(x)
    
def add_rvalue(x):  
    ParsingTmp.rvalues_types.append(x)

def add_keyword(x):
    ''' Declares that x is a keyword --- this is useful to have more
        clear messages. "keywords" are not parsed by Extension.
        (see extensions.py) and allows to have "deep" error indications.
        See http://pyparsing.wikispaces.com/message/view/home/620225
        and the discussion of the "-" operator in the docs.
    '''
    ParsingTmp.keywords.append(x)

W = Where


O = Optional
S = Suppress

number = Word(nums) 
point = Literal('.')
e = CaselessLiteral('E')
plusorminus = Literal('+') | Literal('-')
integer = Combine(O(plusorminus) + number)
floatnumber = Combine(integer + O(point + O(number)) + O(e + integer))
integer.setParseAction(lambda tokens: SimpleRValue(int(tokens[0])))
floatnumber.setParseAction(lambda tokens: SimpleRValue(float(tokens[0])))

isnumber = lambda x: isinstance(x, Number)

rvalue = Forward()
rvalue.setName('rvalue')
contract = Forward()
contract.setName('contract')
simple_contract = Forward()
simple_contract.setName('simple_contract')

# Import all expressions -- they will call add_contract() and add_rvalue()
from .library import (EqualTo, Unary, Binary, composite_contract,
                      identifier_contract, misc_variables_contract,
                      int_variables_contract, int_variables_ref,
                      misc_variables_ref, SimpleRValue)

#operand_no_var_ref = integer | floatnumber | MatchFirst(ParsingTmp.rvalues_types)
#rvalue_no_var_ref = operatorPrecedence(operand_no_var_ref, [
#             ('-', 1, opAssoc.RIGHT, Unary.parse_action),
#             ('*', 2, opAssoc.LEFT, Binary.parse_action),
#             ('-', 2, opAssoc.LEFT, Binary.parse_action),
#             ('+', 2, opAssoc.LEFT, Binary.parse_action),
#          ])


add_rvalue(int_variables_ref)
add_rvalue(misc_variables_ref)

operand = integer | floatnumber | MatchFirst(ParsingTmp.rvalues_types)
operand.setName('r-value')

operatorPrecedence = myOperatorPrecedence
rvalue << operatorPrecedence(operand, [
             ('-', 1, opAssoc.RIGHT, Unary.parse_action),
             ('*', 2, opAssoc.LEFT, Binary.parse_action),
             ('-', 2, opAssoc.LEFT, Binary.parse_action),
             ('+', 2, opAssoc.LEFT, Binary.parse_action),
          ])

# I want 
# - BindVariable to have precedence to EqualTo(VariableRef)
# but I also want:
# - Arithmetic to have precedence w.r.t BindVariable 
# last is variables
add_contract(misc_variables_contract)
add_contract(int_variables_contract)
add_contract(rvalue.copy().setParseAction(EqualTo.parse_action))

# Try to parse the string normally; then try identifiers
hardwired = MatchFirst(ParsingTmp.contract_types)

hardwired.setName('Predefined contract expression')
simple_contract << (hardwired | identifier_contract)
simple_contract.setName('simple contract expression')

any_contract = composite_contract | simple_contract
any_contract.setName('Any simple or composite contract')
contract << (any_contract) # Parentheses before << !!
