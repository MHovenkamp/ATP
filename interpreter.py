# token types
RESERVED, INT, ID ="RESERVED", "INT", "ID"

class Token:
    def __init__(self, value, value_type):
        # token text
        self.value = value
        # type of token
        self.value_type = value_type

    def __str__(self):
        return 'Token({value}, {value_type})'.format(
            value=self.value,
            value_type=self.value_type
        )

    def __repr__(self):
        return self.__str__()

class Interpreter:
    def __init__(self, code_file_name):
        self.code_file_name = code_file_name
        self.tokens = []

    def lexen(self):
        code = open(self.code_file_name, "r")
        self.code_text = code.read()
        operators = "+-/*"
        for item in self.code_text.split():
            if item == "FROM":
                self.tokens.append(Token(item, RESERVED))
            elif item == "TO":
                self.tokens.append(Token(item, RESERVED))
            elif item in operators:
                self.tokens.append(Token(item, RESERVED))
            elif item.isnumeric():
                self.tokens.append(Token(item, INT))
            else:
                self.tokens.append(Token(item, ID))

        return self.tokens

def main():
    test = Interpreter("code.txt")
    print(test.lexen())

main()