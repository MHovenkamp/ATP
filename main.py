import lexer
import parser
import enums

def main():
    lexed = lexer.lexen("code.txt")
    parse = parser.Parser()
    tree, found_funcs = parse.parse(lexed)
    print(found_funcs)
    # for item in tree:
    #     print(item)

    if len(tree) == 1 and type(tree[0]) == parser.Error:
        print(tree[0])
    else:
        visitor = parser.Visitor()
        tree = visitor.visitAl(tree, found_funcs=found_funcs)
        if type(tree) is parser.Error:
            print(tree)
main()