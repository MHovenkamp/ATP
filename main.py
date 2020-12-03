import lexer
import parser
import enums

def main():
    lexed = lexer.lexen("code.txt")
    parse = parser.Parser()
    tree = parse.parse(lexed)
    # for item in tree:
    #     print(item.fu)

    if len(tree) == 1 and type(tree[0]) == parser.Error:
        print(tree[0])
    else:
        visitor = parser.Visitor()
        tree = visitor.visitAl(tree, tree)
        if type(tree) is parser.Error:
            print(tree)
main()