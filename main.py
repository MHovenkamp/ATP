import interpreter
import parser
import enums

def main():
    inter = interpreter.Interpreter("code.txt")
    lexed = inter.lexen()
    for value in lexed:
        print(value)
    # parse = parser.Parser(lexed)
    # parse.parse(lexed)
    
main()