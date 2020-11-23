import parser
import lexer
from typing import TypeVar, List, Callable

A = TypeVar('A')
B = TypeVar('B')
def map(f : Callable[[A], B], lijst : List[A])-> List[B]:
    if len(lijst) == 0:
        return[]
    else:
        head, *tail = lijst
        return [f(head)] + map(f,tail)

A = TypeVar(parser.VariableNode)
B = TypeVar(parser.VariableNode)
C = TypeVar(parser.VariableNode)

def zipWith(f : Callable[[A, B], C], xs : List[A],ys : List[B])-> List[C]:
    if len(xs) == 0 or len(ys) == 0:
        return[]
    else:
        x, *xrest = xs
        y, *yrest = ys
    return[f(x,y)] + zipWith(f, xrest, yrest)