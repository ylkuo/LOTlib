"""
String operations that are a little safer than defaults, and which mimic cons/cdr/car (for doing grammar induction)
"""
from LOTlib.Eval import primitive, RecursionDepthException

class StringLengthException(Exception):
    """ When strings get too long """
    MAX_LENGTH = 256
    pass

@primitive
def strcons_(*x, **kwargs):
    for xi in x:
        if len(xi) > StringLengthException.MAX_LENGTH:
            raise StringLengthException

    return kwargs.get('sep','').join(x)

@primitive
def strcar_(x):
    if len(x) == 0:
        return ''
    else:
        return x[0]

@primitive
def strcdr_(x):
    if len(x) == 0:
        return ''
    else:
        return x[1:]


