from typing import List
import operator
import enums

class Token(object):
    def __init__(self, value: str, value_type: enums.token_types):
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
    def __init__(self, code_file_name):
        self.code_file_name = code_file_name
        self.tokens = []

    def __lexCreateTokens(self, seperate_words : List[str]):
        if len(seperate_words) == 0:
            return 0
        head, *tail = seperate_words
        
        if head == enums.token_types.FROM.name:
            self.tokens.append(Token(head, enums.token_types.FROM))
        elif head == enums.token_types.TO.name:
            self.tokens.append(Token(head, enums.token_types.TO))
        elif head == enums.token_types.LINE.name:
            self.tokens.append(Token(head, enums.token_types.LINE))
        elif head == enums.token_types.IN.name:
            self.tokens.append(Token(head, enums.token_types.IN))
        elif head == enums.token_types.OUT.name:
            self.tokens.append(Token(head, enums.token_types.OUT))
        elif head == enums.token_types.ERR.name:
            self.tokens.append(Token(head, enums.token_types.ERR))
        elif head == enums.token_types.OUTPUT.name:
            self.tokens.append(Token(head, enums.token_types.OUTPUT))
        elif head == enums.token_types.DECLARE.name:
            self.tokens.append(Token(head, enums.token_types.DECLARE))
        elif head == enums.token_types.INPUT.name:
            self.tokens.append(Token(head, enums.token_types.INPUT))
        elif head == enums.token_types.START.name:
            self.tokens.append(Token(head, enums.token_types.START))
        elif head == enums.token_types.END.name:
            self.tokens.append(Token(head, enums.token_types.END))
        elif head == "+":
            self.tokens.append(Token(head, enums.token_types.ADD))
        elif head == "-":
            self.tokens.append(Token(head, enums.token_types.SUB))
        elif head == "*":
            self.tokens.append(Token(head, enums.token_types.MUL))
        elif head == "/":
            self.tokens.append(Token(head, enums.token_types.DIV))
        elif head.isnumeric():
            self.tokens.append(Token(head, enums.token_types.INT))
        elif head == enums.token_types.IF.name:
            self.tokens.append(Token(head, enums.token_types.IF))
        elif "\"" in head:
            self.tokens.append(Token(head, enums.token_types.STRING))
        elif "<" in head:
            self.tokens.append(Token(head, enums.token_types.SMALLER))
        elif ">" in head:
            self.tokens.append(Token(head, enums.token_types.GREATER))
        elif "==" in head:
            self.tokens.append(Token(head, enums.token_types.EQUAL))
        elif "!=" in head:
            self.tokens.append(Token(head, enums.token_types.NOTEQUAL))
        elif "<=" in head:
            self.tokens.append(Token(head, enums.token_types.EQUALSMALLER))
        elif ">=" in head:
            self.tokens.append(Token(head, enums.token_types.EQUALGREATER))
        else:
            self.tokens.append(Token(head, enums.token_types.VAR))

        return self.__lexCreateTokens(tail)

    def lexen(self):
        code = open(self.code_file_name, "r")
        self.code_text = code.read()
        seperate_words = self.code_text.split()
        self.__lexCreateTokens(seperate_words)
        return self.tokens
