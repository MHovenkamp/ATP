from typing import List, TypeVar
import functools
import operator

import enums
import lexer

# base node / literal node
lit_types = TypeVar('lite_types', int, str)
class Node(object):
    def __init__(self, value : lit_types, line_nr: int,token_type : enums.token_types, node_type : enums.node_types=enums.node_types.BASE):
        self.value = value
        self.token_type = token_type
        self.node_type = node_type
        self.line_nr = line_nr
    def __str__(self):
        return '{value}'.format(
            value=self.value
        )

    def __repr__(self):
        return self.__str__()

    def visit(self):
        visitor = Visitor()
        return visitor.visitNode(self)

class VariableNode(Node):
    def __init__(self, variable_name : str, value : Node, line_nr: int, token_type , node_type : enums.node_types=enums.node_types.VAR):
        super().__init__(value, line_nr, token_type, node_type)
        self.variable_name = variable_name

    def __str__(self):
        return '[{line_nr}] {variable_name}={value}'.format(
            line_nr = self.line_nr,
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
    def __init__(self, value : Node, rhs : int, line_nr: int, token_type = enums.token_types, node_type : enums.node_types=enums.node_types.MATH):
        super().__init__(value, line_nr, token_type, node_type)
        self.rhs = rhs
    
    def __str__(self):
        return '[{line_nr}] MathNode( {value}, {token_type} ,{rhs})'.format(
            line_nr = self.line_nr,
            value = self.value.__repr__(),
            token_type = self.token_type,
            rhs = self.rhs
        )
    def __repr__(self):
        return self.__str__()

    def visit(self):
        visitor = Visitor()
        return visitor.visitMath(self)

class ConditionNode(Node):
    def __init__(self, value : Node, condition : Node, line_nr : int, token_type = enums.token_types, node_type: enums.node_types=enums.node_types.CONDITION):
        super().__init__(value, line_nr, token_type, node_type)
        self.condition = condition

    def __str__(self):
        return '({value} {token_type}, {condition})'.format(
            value = self.value.__repr__(),
            token_type = self.token_type,
            condition = self.condition.__repr__()
        )

    def __repr__(self):
        return self.__str__()

    def visit(self):
        visitor = Visitor()
        return visitor.visitCondition(self)

class IfNode(Node):
    def __init__(self, value : Node, condition : ConditionNode, new_value : Node, line_nr : int, token_type = enums.token_types, node_type: enums.node_types=enums.node_types.IF):
        super().__init__(value, line_nr, token_type, node_type)
        self.condition = condition
        self.new_value = new_value
    
    def __str__(self):
        return '[{line_nr}] IfNode({value}, condition: {condition}, -> {new_value})'.format(
            line_nr = self.line_nr,
            value = self.value.__repr__(),
            condition = self.condition.__repr__(),
            new_value = self.new_value
        )

    def __repr__(self):
        return self.__str__()

    def visit(self):
        visitor = Visitor()
        return visitor.visitIF(self)

class Parser(object):
    def __init__(self, tokens : List[lexer.Token], types : enums.token_types = None):
        self.tokens = tokens
        self.token_index = 0
        self.state = enums.parser_states.IDLE

    list_types = TypeVar(Node, VariableNode, MathNode)
    def parse(self, token_list : List[lexer.Token], line_nr : int = 1, found_vars : List[VariableNode]=[], tree : List[list_types] = []):
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
                    # check if y variable is an assignable value
                    if found_line[3].token_type == enums.token_types.VAR or found_line[3].token_type == enums.token_types.OUT:
                        # check if y var already exists
                        check_exist_y = self.findAndReturn(found_vars, found_line[3].value)
                        if len(check_exist_y) == 0:
                            #variable does not exist yet
                            #check if var x already exists
                            if found_line[1].token_type == enums.token_types.VAR:
                                check_exist_x = self.findAndReturn(found_vars, found_line[1].value)
                                if len(check_exist_x) == 1:
                                    var = VariableNode(found_line[3].value, check_exist_x[0], line_nr, enums.token_types.VAR)
                                else:
                                    print("error trying to assign var that does not exist, or double var")
                            elif found_line[1].token_type == enums.token_types.INT:
                                var = VariableNode(found_line[3].value, Node(found_line[1].value, line_nr, enums.token_types.INT), line_nr, enums.token_types.VAR)
                            elif found_line[1].token_type == enums.token_types.STRING:
                                var = VariableNode(found_line[3].value, Node(found_line[1].value, line_nr, enums.token_types.STRING), line_nr, enums.token_types.VAR)
                        elif len(check_exist_y) == 1:
                            #variable does exist
                            #check if var x already exists
                            if found_line[1].token_type == enums.token_types.VAR:
                                check_exist_x = self.findAndReturn(found_vars, found_line[1].value)
                                if len(check_exist_x) == 1:
                                    check_exist_y[0].value = check_exist_x[0]
                                    check_exist_y[0].line_nr = line_nr
                                    var = check_exist_y[0]
                                else:
                                    print("error trying to assign var that does not exist, or double var")
                            elif found_line[1].token_type == enums.token_types.INT:
                                check_exist_y[0].value = Node(found_line[1].value, line_nr, enums.token_types.INT)
                                check_exist_y[0].line_nr = line_nr
                                var = check_exist_y[0]
                            elif found_line[1].token_type == enums.token_types.STRING:
                                check_exist_y[0].value = Node(found_line[1].value, line_nr, enums.token_types.STRING)
                                check_exist_y[0].line_nr = line_nr
                                var = check_exist_y[0]
                        else:
                            print("hier komt ene error")

                    if found_line[3].token_type == enums.token_types.OUT:
                        var.token_type = enums.token_types.OUT
                    if var.token_type != enums.token_types.OUT:
                        found_vars.append(var)
                    tree.append(var)
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
                                        nmbr = Node(found_line[5].value, line_nr, found_line[5].token_type, enums.node_types.BASE)
                                        if len(var) == 0:
                                            print("Math on unknown variable")
                                        if len(var) == 1:
                                            math = MathNode(var[0], nmbr, line_nr, found_line[4].token_type)
                                            tree.append(math)
                                    if (found_line[5].token_type is enums.token_types.VAR):
                                        var1 = self.findAndReturn(found_vars, found_line[1].value)
                                        var2 = self.findAndReturn(found_vars, found_line[5].value)
                                        if len(var1) == 0 or len(var2) == 0:
                                            print("Math on unknown variable")
                                        if len(var1) == 1 and len(var2) == 1:
                                            math = MathNode(var1[0], var2[0], line_nr, found_line[4].token_type)
                                            tree.append(math)
                elif length_line == 7:
                    #check for if
                    if found_line[1].token_type == enums.token_types.VAR and found_line[5].token_type == enums.token_types.IF:
                        if (found_line[3].token_type == enums.token_types.EQUAL or
                            found_line[3].token_type == enums.token_types.NOTEQUAL or
                            found_line[3].token_type == enums.token_types.GREATER or
                            found_line[3].token_type == enums.token_types.SMALLER or
                            found_line[3].token_type == enums.token_types.EQUALGREATER or
                            found_line[3].token_type == enums.token_types.EQUALSMALLER):
                                check_exist_value = self.findAndReturn(found_vars, found_line[1].value)

                                if len(check_exist_value) == 0 or len(check_exist_value) > 1:
                                    print("value to if on does not exist")
                                else:
                                    if found_line[4].token_type == enums.token_types.VAR:
                                        check_exist_condition = self.findAndReturn(found_vars, found_line[4].value)
                                        if check_exist_condition is None:
                                            print("error condition does not exist")
                                        else:
                                            condition = ConditionNode(check_exist_value[0], check_exist_condition[0], line_nr, found_line[3].token_type)
                                    elif found_line[4].token_type == enums.token_types.INT:
                                        condition = ConditionNode(check_exist_value[0], Node(found_line[4].value, line_nr, enums.token_types.INT), line_nr, found_line[3].token_type)
                                    elif found_line[4].token_type == enums.token_types.STRING:
                                        condition = ConditionNode(check_exist_value[0], Node(found_line[4].value, line_nr, enums.token_types.STRING), line_nr, found_line[3].token_type)

                                    if found_line[6].token_type == enums.token_types.VAR:
                                        check_exist_new_value = self.findAndReturn(found_vars, found_line[6].value)
                                        if check_exist_new_value is None:
                                            print("error new value does not exist")
                                        else:
                                            new_value = check_exist_new_value[0]
                                    elif found_line[6].token_type == enums.token_types.INT:
                                        new_value = Node(found_line[6].value, line_nr, enums.token_types.INT)
                                    elif found_line[6].token_type == enums.token_types.STRING:
                                        new_value = Node(found_line[6].value, line_nr, enums.token_types.STRING)
                                    
                                    var = IfNode(check_exist_value[0], condition, new_value, line_nr, enums.token_types.IF)
                                    tree.append(var)
                                

                remaining_tail = tail[length_line-1:]
        return self.parse(remaining_tail, line_nr+1, found_vars, tree)
                
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
        node.value.line_nr = node.line_nr
        node.value.value = Node(functools.reduce(function, items), node.line_nr, enums.token_types.INT) #HOGERE ORDE FUNCTIE

    #TODO FIX IF STATEMENTS
    def visitCondition(self, node : ConditionNode):
        if node.token_type == enums.token_types.GREATER:
            function = lambda x,y: True if x > y else False
        elif node.token_type == enums.token_types.SMALLER:
            function = lambda x,y: True if x < y else False
        elif node.token_type == enums.token_types.EQUAL:
            function = lambda x,y: True if x == y else False
        elif node.token_type == enums.token_types.EQUALGREATER:
            function = lambda x,y: True if x >= y else False
        elif node.token_type == enums.token_types.EQUALSMALLER:
            function = lambda x,y: True if x <= y else False
        elif node.token_type == enums.token_types.NOTEQUAL:
            function = lambda x,y: True if x != y else False

        items = [node.value, node.condition]
        if node.value.token_type == enums.token_types.STRING and node.condition.token_type == enums.token_types.STRING:
            if (node.token_type == enums.token_types.EQUAL or
                node.token_type == enums.token_types.NOTEQUAL):
                result = functools.reduce(function, items)
                print(result)
                return result
        if node.value.token_type == enums.token_types.INT and node.condition.token_type == enums.token_types.INT:
            items = list(map(lambda x: int(x) if x.isnumeric() else x, items))
            result = functools.reduce(function, items)
            print(result)
            return result

    def visitIF(self, node : IfNode):
        if node.condition.visit() == True:
            node.value.value = Node(node.new_value, node.line_nr, node.value.as_integer_ratiotoken_type)

            
