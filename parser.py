from typing import List, TypeVar
import functools
import operator

import enums
import lexer

# base node / literal node
lit_types = TypeVar('lite_types', int, str)
class Node(object):
    def __init__(self, value : lit_types, token_type : enums.token_types, node_type : enums.node_types=enums.node_types.BASE):
        self.value = value
        self.token_type = token_type
        self.node_type = node_type
    def __str__(self):
        return '{value}'.format(
            value=self.value,
        )

    def __repr__(self):
        return self.__str__()

    def visit(self):
        visitor = Visitor()
        return visitor.visitNode(self)

class VariableNode(Node):
    def __init__(self, variable_name : str, value : Node, token_type , node_type : enums.node_types=enums.node_types.VAR):
        super().__init__(value, token_type, node_type)
        self.variable_name = variable_name

    def __str__(self):
        return 'VariableNode({variable_name},{value})'.format(
            value = self.value.__repr__(),
            variable_name = self.variable_name
        )
    
    def __repr__(self):
        return self.__str__()

    def visit(self):
        visitor = Visitor()
        return visitor.visitVariable(self)

class MathNode(Node):
    # value = variable to change
    # rhs = int to change it with
    def __init__(self, value : Node, rhs : int, token_type = enums.token_types, node_type : enums.node_types=enums.node_types.MATH):
        super().__init__(value, token_type, node_type)
        self.rhs = rhs
    
    def __str__(self):
        return 'MathNode({value}, {token_type} ,{rhs})'.format(
            value = self.value.__repr__(),
            token_type = self.token_type,
            rhs = self.rhs
        )
    def __repr__(self):
        return self.__str__()

    def visit(self):
        visitor = Visitor()
        return visitor.visitMath(self)


class Parser(object):
    def __init__(self, tokens : List[lexer.Token], types : enums.token_types = None):
        self.tokens = tokens
        self.token_index = 0
        self.state = enums.parser_states.IDLE

    list_types = TypeVar(Node, VariableNode, MathNode)
    def parse(self, token_list : List[lexer.Token], found_vars : List[VariableNode]=[], tree : List[list_types] = []):
        if len( token_list ) == 0:
            return tree

        head, *tail = token_list

        value = head.value
        token_type = head.token_type
        if self.state == enums.parser_states.IDLE:
            if token_type == enums.token_types.FROM:
                found_line = [head] + self.getLine(tail)
                # based on length of line start assigning
                length_line = len(found_line)
                if found_line[0].token_type != enums.token_types.FROM and found_line[3].token_type != enums.token_types.TO:
                    print("This print later throws an error, invalid syntax")
                if length_line == 4:
                    # check if x variable is an assignable value
                    if found_line[3].token_type == enums.token_types.VAR or found_line[3].token_type == enums.token_types.OUT:
                        if (found_line[1].token_type == enums.token_types.INT or
                            found_line[1].token_type == enums.token_types.STRING):
                            var = VariableNode(found_line[3].value, Node(found_line[1].value, found_line[1].token_type), found_line[3].token_type, enums.node_types.VAR)
                            temp = self.findAndReturn(found_vars, var.variable_name)
                            if len(temp) == 0:
                                found_vars.append(var)
                                tree.append(var)
                            elif len(temp) == 1:
                                # change var object to new value and re-ad to list of vars
                                temp[0].value = Node(found_line[1].value, found_line[1].token_type)
                                tree.append(temp[0])
                            else:
                                print("var has multiple values")
                        if found_line[1].token_type == enums.token_types.VAR:
                            temp = self.findAndReturn(found_vars, found_line[1].value)
                            if len(temp) == 0:
                                print("cant assign empty var to var")
                            if len(temp) == 1:
                                var = VariableNode(found_line[3].value, temp[0], found_line[3].token_type, enums.node_types.VAR)
                                temp2 = self.findAndReturn(found_vars, var.variable_name)
                                if len(temp2) == 0:
                                    found_vars.append(var)
                                    tree.append(var)
                                elif len(temp2) == 1:
                                    # change var object to new value and re-ad to list of vars
                                    temp2[0].value = Node(found_line[1].value, found_line[1].token_type)
                                    tree.append(temp[0])
                                else: 
                                    print("var has multiple values")

                elif length_line == 6:
                    # check for math
                    if found_line[1].token_type == enums.token_types.VAR and found_line[3].token_type == enums.token_types.VAR:
                        if (found_line[4].token_type is enums.token_types.ADD or
                            found_line[4].token_type is enums.token_types.MUL or
                            found_line[4].token_type is enums.token_types.SUB or
                            found_line[4].token_type is enums.token_types.DIV):
                                # comfirm its the same var we are changing
                                if found_line[1].value == found_line[3].value:
                                    if (found_line[5].token_type is enums.token_types.INT):
                                        var = self.findAndReturn(found_vars, found_line[1].value)
                                        nmbr = Node(found_line[5].value, found_line[5].token_type, enums.node_types.BASE)
                                        if len(var) == 0:
                                            print("Math on unknown variable")
                                        if len(var) == 1:
                                            math = MathNode(var[0], nmbr, found_line[4].token_type)
                                            tree.append(math)
                                    if (found_line[5].token_type is enums.token_types.VAR):
                                        var1 = self.findAndReturn(found_vars, found_line[1].value)
                                        var2 = self.findAndReturn(found_vars, found_line[5].value)
                                        if len(var1) == 0 or len(var2) == 0:
                                            print("Math on unknown variable")
                                        if len(var1) == 1 and len(var2) == 1:
                                            math = MathNode(var1[0], var2[0], found_line[4].token_type)
                                            tree.append(math)

                
                remaining_tail = tail[length_line-1:]
        return self.parse(remaining_tail, found_vars, tree)
                
    def getLine(self, tokens : List[lexer.Token], line : List[lexer.Token]=[]):
        
        if len(tokens) == 0:
            return []
        head, *tail = tokens 
        if head.token_type != enums.token_types.FROM:
            return [head] + self.getLine(tail)
        return []

    def findAndReturn(self,  search_area : List[VariableNode], value_to_find : str ):
        if len(search_area) == 0:
            return []
        head, *tail = search_area
        if head.variable_name == value_to_find:
            return [head]
        return [] + self.findAndReturn( tail, value_to_find)

class Visitor(object):
    def __init__(self):
        pass

    def visitNode(self, node : Node):
        return node.value


    def visitVariable(self, node : VariableNode):
        if node.token_type != enums.token_types.OUT:
            return node.value.visit()
        else:
            return node.value.__repr__()

    def visitMath(self, node : MathNode):
        if node.token_type == enums.token_types.ADD:
            function = lambda x, y:x+y
        elif node.token_type == enums.token_types.SUB:
            function = lambda x, y: x-y
        elif node.token_type == enums.token_types.MUL:
            function = lambda x, y: x*y
        elif node.token_type == enums.token_types.DIV:
            function = lambda x, y: x//y
        
        if node.rhs.token_type == enums.token_types.VAR:
            items = [node.value.visit(), node.rhs.value.visit()]
        else:
            items = [node.value.visit(), node.rhs.visit()]

        items = list(map(lambda x: int(x) if x.isnumeric() else x, items)) #HOGERE ORDE FUNCTIE
        node.value.value = Node(functools.reduce(function, items), enums.token_types.INT) #HOGERE ORDE FUNCTIE