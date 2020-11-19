from typing import List
import operator

class Token:
    def __init__(self, value: str, value_type: str):
        self.value = value
        self.value_type = value_type

    def __str__(self):
        return 'Token({value}, {value_type})'.format(
            value=self.value,
            value_type=self.value_type
        )

    def __repr__(self):
        return self.__str__()

class Interpreter(object):
    FROM = "FROM"
    TO = "TO"
    LINE = "LINE"
    OUT = "OUT"
    ERR = "ERR"
    OUTPUT = "OUTPUT"
    DECLARE = "DECLARE"
    INPUT = "INPUT"
    START = "START"
    END = "END"
    INT = "INT"
    STRING = "STRING"
    VAR = "VAR"
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    GREATER = "GREATER"
    SMALLER = "SMALLER"
    EQUAL = "EQUAL"
    EQUALGREATER = "EQUALGREATER"
    EQUALSMALLER = "EQUALSMALLER"
    NOTEQUAL = "NOTEQUAL"
    DIV = "DIV"
    IF = "IF"
    def __init__(self, code_file_name):
        self.code_file_name = code_file_name
        self.tokens = []

    def __lexCreateTokens(self, seperate_words : List[str]):
        if len(seperate_words) == 0:
            return 0
        head, *tail = seperate_words
        
        if head == self.FROM:
            self.tokens.append(Token(head, self.FROM))
        elif head == self.TO:
            self.tokens.append(Token(head, self.TO))
        elif head == self.LINE:
            self.tokens.append(Token(head, self.LINE))
        elif head == self.OUT:
            self.tokens.append(Token(head, self.OUT))
        elif head == self.ERR:
            self.tokens.append(Token(head, self.ERR))
        elif head == self.OUTPUT:
            self.tokens.append(Token(head, self.OUTPUT))
        elif head == self.DECLARE:
            self.tokens.append(Token(head, self.DECLARE))
        elif head == self.INPUT:
            self.tokens.append(Token(head, self.INPUT))
        elif head == self.START:
            self.tokens.append(Token(head, self.START))
        elif head == self.END:
            self.tokens.append(Token(head, self.END))
        elif head == "+":
            self.tokens.append(Token(head, self.ADD))
        elif head == "-":
            self.tokens.append(Token(head, self.SUB))
        elif head == "*":
            self.tokens.append(Token(head, self.MUL))
        elif head == "/":
            self.tokens.append(Token(head, self.DIV))
        elif head.isnumeric():
            self.tokens.append(Token(head, self.INT))
        elif head == self.IF:
            self.tokens.append(Token(head, self.IF))
        elif "\"" in head:
            self.tokens.append(Token(head, self.STRING))
        elif "<" in head:
            self.tokens.append(Token(head, self.SMALLER))
        elif ">" in head:
            self.tokens.append(Token(head, self.GREATER))
        elif "==" in head:
            self.tokens.append(Token(head, self.EQUAL))
        elif "!=" in head:
            self.tokens.append(Token(head, self.NOTEQUAL))
        elif "<=" in head:
            self.tokens.append(Token(head, self.EQUALSMALLER))
        elif ">=" in head:
            self.tokens.append(Token(head, self.EQUALGREATER))
        else:
            self.tokens.append(Token(head, self.VAR))

        return self.__lexCreateTokens(tail)

    def lexen(self):
        code = open(self.code_file_name, "r")
        self.code_text = code.read()
        seperate_words = self.code_text.split()
        self.__lexCreateTokens(seperate_words)
        return self.tokens
