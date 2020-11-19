from typing import List
import operator

import interpreter


class Parser(object):
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
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = 0

    def parse(self, token_list : List[interpreter.Token] ):
        if len(token_list) == 0:
            return 0
        head, *tail = token_list
        token_type = head.value_type
        token_value = head.value

        # check if variable assignment
        # statements van 4 lang:
        #   simple assignement to a variable
        #   printing to screen or throwing error
        #   taking input from user
        #   jumping to line number


        if token_type == self.FROM and token_value == self.FROM:
            if tail[0].value_type == self.INT or tail[0].value_type == self.STRING or tail[0].value_type == self.VAR:
                if tail[1].value_type == self.TO:
                    if tail[2].value_type == self.VAR:
                        self.variable_assignement(tail)
                        if len(tail) > 3:
                            if tail[3].value_type != self.FROM:
                                if tail[3].value in "+-/*":
                                    if tail[4].value_type == self.INT or tail[4].value_type == self.VAR:
                                        self.math_assignement(tail)
                            else:
                                self.variable_assignement(tail)
                        else
        
        print(token_type, token_value)
        return self.parse(tail)

    def variable_assignement(self, token_list: List[interpreter.Token] ):
        print("----------------------------")
        print( "found variable assignement ")
        print( token_list[0].value, token_list[1].value, token_list[2].value)
        print("----------------------------")
        
    def math_assignement(self, token_list: List[interpreter.Token] ):
        print("----------------------------")
        print( "found math assignement ")
        print( token_list[0].value, token_list[1].value, token_list[2].value, token_list[3].value, token_list[4].value)
        print("----------------------------")