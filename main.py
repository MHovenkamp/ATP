import interpreter
import parser
import enums

def main():
    inter = interpreter.Interpreter("code.txt")
    lexed = inter.lexen()
    print("------lexed code-----")
    for value in lexed:
        print(value)
    print("---------------------")
    parse = parser.Parser(lexed, enums.token_types)
    parse.parse(lexed)
    
main()