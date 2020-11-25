from enum import Enum

class token_types(Enum):
    FROM = "FROM"
    TO = "TO"
    LINE = "LINE"
    IN = "IN"
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

class parser_states(Enum):
    IDLE = "IDLE"

class node_types(Enum):
    BASE = "BASE"
    MATH = "MATH"
    VAR = "VAR"
    IF = "IF"
    CONDITION = "CONDITION"