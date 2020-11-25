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
    for item in result:
        print(item)
        if item.token_type == enums.token_types.OUT:
            print(item.visit())
        else:
            item.visit()
    
main()