import lexer
import parser
import enums

def main():
    lexed = lexer.lexen("code.txt")
    # print("------lexed code-----")
    # for value in lexed:
    #     print(value)
    # print("---------------------")
    parse = parser.Parser()
    tree = parse.parse(lexed)

    if len(tree) == 1 and type(tree[0]) == parser.Error:
        print(tree[0])
    else:
        visitor = parser.Visitor()
        tree = visitor.visitAl(tree, tree)
        # if len(tree) == 1:
        #     print(tree)
        # else:
        #     for item in tree:
        #         print(item)
main()