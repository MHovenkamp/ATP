from typing import List
import operator
import enums
import interpreter

class Node(object):
    def __init__(self, value : str, token_type : enums.token_types, node_type : enums.node_types = enums.node_types.BASE):
        self.value = value
        self.node_type = node_type

    def __str__(self):
        return 'Node({value}, {node_type})'.format(
            value=self.value,
            node_type=self.node_type
        )

    def __repr__(self):
        return self.__str__()

class MathNode(Node):
    def __init__(self, value : str, token_type : enums.token_types, rhs : str, lhs : str, node_type : enums.node_types = enums.node_types.MATH):
        super().__init__(value, token_type, node_type)
        self.rhs = rhs # number to use with operator
        self.lhs = lhs # variable to be changed
    
    def __str__(self):
        return 'MathNode({lhs}, {value}, {rhs})'.format(
            value = self.value,
            lhs = self.lhs,
            rhs = self.rhs
        )
    def __repr__(self):
        return self.__str__()

class VariableNode(Node):
    def __init__(self, value : str, token_type, variable_name : str, node_type : enums.node_types = enums.node_types.VAR):
        super().__init__(value, token_type, node_type)
        self.variable_name = variable_name

    def __str__(self):
        return 'ValueNode({variable_name},{value})'.format(
            value = self.value,
            variable_name = self.variable_name
        )
    
    def __repr__(self):
        return self.__str__()

class Parser(object):
    def __init__(self, tokens : List[interpreter.Token], types : enums.token_types = None):
        self.tokens = tokens
        self.token_index = 0
        self.state = enums.parser_states.IDLE
        self.tree = []

    def parse(self, token_list : List[interpreter.Token]):
        if len( token_list ) == 0:
            return

        head, *tail = token_list
        passed_indexes = 0

        value = head.value
        token_type = head.value_type
        if self.state == enums.parser_states.IDLE:
            if token_type == enums.token_types.FROM:
                found_line = [head] + self.getLine(tail)
                # based on length of line start assigning
                length_line = len(found_line)
                print(length_line)
                if length_line == 4:
                    if found_line[0].value_type != enums.token_types.FROM and found_line[3].value_type != enums.token_types.TO:
                        print("THis print later throws an error, invalid syntax")
                    # check if x variable is an assignable value
                    if (found_line[1].value_type == enums.token_types.VAR or
                        found_line[1].value_type == enums.token_types.INT or
                        found_line[1].value_type == enums.token_types.STRING or
                        found_line[1].value_type == enums.token_types.IN):
                        if found_line[3].value_type == enums.token_types.VAR:
                            # The line assigns a value to a variable
                            self.tree.append(VariableNode(found_line[1].value, enums.token_types.VAR, found_line[3].value, enums.node_types.VAR))
                            for item in self.tree:
                                print(item)
                if length_line == 6:
                    if found_line[1].value_type == enums.token_types.VAR and found_line[3].value_type == enums.token_types.VAR:
                        # comfirm its the same var we are changing
                        if found_line[1].value == found_line[3].value:
                            # self.tree.append(MathNode(found_line[4].value, found_line[4].value_type))
                            print("MATH")

                remaining_tail = tail[length_line-1:]
        return self.parse(remaining_tail)
                
    def getLine(self, tokens : List[interpreter.Token], line : List[interpreter.Token]=[]):
        
        if len(tokens) == 0:
            return []
        head, *tail = tokens 
        if head.value_type != enums.token_types.FROM:
            return [head] + self.getLine(tail)
        return []