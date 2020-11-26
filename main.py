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
    result = parse.parse(lexed)
    for item in result:
        print(item)

    visitor = parser.Visitor()
    tree = visitor.visitAl(result)
    # for item in tree:
    #     print(item)
main()