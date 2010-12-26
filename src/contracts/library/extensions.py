from ..interface import Contract, ContractNotRespected, describe_value
from ..syntax import (Combine, Word, W, alphas, alphanums, oneOf,
                      ParseFatalException, ParseException)

from contracts.syntax import ParsingTmp

class Extension(Contract):
    
    registrar = {}
    
    def __init__(self, identifier, where=None):
        assert identifier in Extension.registrar
        self.identifier = identifier
        Contract.__init__(self, where)
    
    def __str__(self):
        return self.identifier
    
    def __repr__(self):
        return "Extension(%r)" % self.identifier
    
    def check_contract(self, context, value):
        Extension.registrar[self.identifier]._check_contract(context, value)
        
    @staticmethod
    def parse_action(s, loc, tokens):
        identifier = tokens[0]
        
        where = W(s, loc)
        if identifier in ParsingTmp.keywords:
            raise ParseException('Not matching %r' % identifier)
        
        if not identifier in Extension.registrar:
            msg = 'Invalid expression identifier %r.\n' % identifier
            msg += 'I know: %r.\n' % (list(Extension.registrar.keys()))
            msg += str(where)
            # print msg
            raise ParseFatalException(msg)
        
        return Extension(identifier, where)


class CheckCallable(Contract):
    def __init__(self, callable):
        self.callable = callable
        
    def check_contract(self, context, value):
        allowed = (ValueError, AssertionError)
        try:
            result = self.callable(value)
        except allowed as e: # failed
            raise ContractNotRespected(self, str(e), value, context)
            
        if result in [None, True]: 
            # passed
            pass
        elif result == False:
            msg = ('Value does not pass criteria of %s() (module: %s).' % 
                   (self.callable.__name__, self.callable.__module__))
            raise ContractNotRespected(self, msg, value, context)
        else:
            msg = ('I expect that %r returns either True, False, None; or '
                   'raises a ValueError exception. Instead, I got %s.' % 
                   (self.callable, describe_value(value))) 
            raise ValueError(msg)
        
    def __repr__(self):
        ''' Note: this contract is not representable, but anyway it is only used
            by Extension, which serializes using the identifier. '''
        return 'CheckCallable(%r)' % self.callable
 
    def __str__(self):
        ''' Note: this contract is not representable, but anyway it is only used
            by Extension, which serializes using the identifier. '''
        return 'function %s()' % self.callable.__name__
    

#lowercase = alphas.lower()
identifier_expression = Combine(oneOf(list(alphas)) + Word('_' + alphanums))

identifier_contract = identifier_expression.copy().setParseAction(Extension.parse_action)
