import lexer
import parser
import enums

def main():
    lexed = lexer.lexen("code.txt")
    print("------lexed code-----")
    for value in lexed:
        print(value)
    print("---------------------")
    parse = parser.Parser(lexed, enums.token_types)
    result = parse.parse(lexed)
    visitor = parser.Visitor()
    tree = visitor.visitAl(result)
    for item in tree:
        print(item)
main()