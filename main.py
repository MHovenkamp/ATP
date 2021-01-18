import lexer
import parser
import enums
import support

def main():
    lexed = lexer.lexen("test_subroutines_1.txt")
    parse = parser.Parser()
    tree, found_funcs = parse.parse(lexed)

    if len(tree) == 1 and type(tree[0]) == support.Error:
        print(tree[0])
    else:
        visitor = support.Visitor()
        tree = visitor.visitAl(tree, tree, found_funcs=found_funcs)
        if type(tree) is support.Error:
            print(tree)
main()