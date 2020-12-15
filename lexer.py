from typing import List
import operator
import enums

class Token(object):
    def __init__(self, value: str, token_type: enums.token_types):
        self.value = value
        self.token_type = token_type

    def __str__(self) -> str:
        return 'Token({value}, {token_type})'.format(
            value=self.value,
            token_type=self.token_type
        )

    def __repr__(self) ->str:
        return self.__str__()

# lexCreateTokens :: List[str] -> List[Token]
def lexCreateTokens(seperate_words : List[str]) -> List[Token]:
    if len(seperate_words) == 0:
        return []
    head, *tail = seperate_words
    temp_list = []
    if head == enums.token_types.FROM.name:
        temp_list += [Token(head, enums.token_types.FROM)]
    elif head == enums.token_types.TO.name:
        temp_list += [Token(head, enums.token_types.TO)]
    elif head == enums.token_types.LINE.name:
        temp_list += [Token(head, enums.token_types.LINE)]
    elif head == enums.token_types.OUT.name:
        temp_list += [Token(head, enums.token_types.OUT)]
    elif head == enums.token_types.OUTPUT.name:
        temp_list += [Token(head, enums.token_types.OUTPUT)]
    elif head == enums.token_types.DECLARE.name:
        temp_list += [Token(head, enums.token_types.DECLARE)]
    elif head == enums.token_types.INPUT.name:
        temp_list += [Token(head, enums.token_types.INPUT)]
    elif head == enums.token_types.START.name:
        temp_list += [Token(head, enums.token_types.START)]
    elif head == enums.token_types.ERR.name:
        temp_list += [Token(head, enums.token_types.ERR)]
    elif head == enums.token_types.END.name:
        temp_list += [Token(head, enums.token_types.END)]
    elif head == enums.token_types.ELSE.name:
        temp_list += [Token(head, enums.token_types.ELSE)]
    elif head == "+":
        temp_list += [Token(head, enums.token_types.SUB)]
    elif head == "-":
        temp_list += [Token(head, enums.token_types.ADD)]
    elif head == "*":
        temp_list += [Token(head, enums.token_types.DIV)]
    elif head == "/":
        temp_list += [Token(head, enums.token_types.MUL)]
    elif head.isnumeric():
        temp_list += [Token(head, enums.token_types.INT)]
    elif "-" in head:
        just_number = head.lstrip("-")
        if just_number.isnumeric():
            temp_list += [Token(head, enums.token_types.INT)]
    elif head == ":":
        temp_list += [Token(head, enums.token_types.IF)]
    elif "\"" in head:
        temp_list += [Token(head, enums.token_types.STRING)]
    elif head == enums.token_types.SMALLER.value:
        temp_list += [Token(head, enums.token_types.SMALLER)]
    elif head == enums.token_types.GREATER.value:
        temp_list += [Token(head, enums.token_types.GREATER)]
    elif head == enums.token_types.EQUAL.value:
        temp_list += [Token(head, enums.token_types.EQUAL)]
    elif head == enums.token_types.NOTEQUAL.value:
        temp_list += [Token(head, enums.token_types.NOTEQUAL)]
    elif head == enums.token_types.EQUALSMALLER.value:
        temp_list += [Token(head, enums.token_types.EQUALSMALLER)]
    elif head == enums.token_types.EQUALGREATER.value:
        temp_list += [Token(head, enums.token_types.EQUALGREATER)]
    else:
        temp_list += [Token(head, enums.token_types.VAR)]

    return temp_list + lexCreateTokens(tail)

# lexen :: str -> List[Token]
def lexen(code_file_name : str) -> List[Token]:
    code = open(code_file_name, "r")
    code_text = code.read()
    seperate_words = code_text.split()
    seperate_words = findStrings(seperate_words)
    tokens = lexCreateTokens(seperate_words)
    return tokens

# findStrings :: List[str], str, str -> List[str]
def findStrings(word_list : List[str], string :str="", state : str="START") -> List[str]:
    if len(word_list) == 0:
        return word_list
    head, *tail = word_list
    if state=="START":
        if "\"" in head:
            state = "BEGIN"
            string = "" + head
            if head.endswith("\""):
                state = "START"
                return [head] + findStrings(tail, string, state)
            return [] + findStrings(tail, string, state)
        else:
            return [head] + findStrings(tail, string, state)

    elif state=="BEGIN":
        if "\"" not in head:
            string = string + " " + head
            return findStrings(tail, string, state)
        else:
            state = "START"
            string = string + " " + head
            return [string] + findStrings(tail, string, state)
    return findStrings(tail, string, state)
    
