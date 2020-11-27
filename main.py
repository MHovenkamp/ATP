import lexer
import parser
import enums

def main():
    lexed = lexer.lexen("code.txt")
    print("------lexed code-----")
    for value in lexed:
        print(value)
    print("---------------------")
    parse = parser.Parser()
    tree = parse.parse(lexed)
    for token in tree:
        print(token)

    # visitor = parser.Visitor()
    # tree = visitor.visitAl(result)
    # for item in tree:
    #     print(item)
main()