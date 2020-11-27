from typing import List, TypeVar
import functools
import operator
import copy

import enums
import lexer

#TODO functie: IN en output functies, GOTO statements, error handling

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

    def __repr__(self) -> str:
        return self.__str__()

    def visit(self) -> lit_types:
        visitor = Visitor()
        return visitor.visitNode(self)

class VariableNode(Node):
    def __init__(self, variable_name : str, value : Node, line_nr: int, token_type , node_type : enums.node_types=enums.node_types.VAR):
        super().__init__(value, line_nr, token_type, node_type)
        self.variable_name = variable_name

    def __str__(self) -> str:
        return '[{line_nr}] {variable_name}={value}'.format(
            line_nr = self.line_nr,
            value = self.value.__repr__(),
            variable_name = self.variable_name
        )
    
    def __repr__(self) -> str:
        return self.__str__()

    def visit(self) -> Node:
        visitor = Visitor()
        return visitor.visitVariable(self)

class MathNode(Node):
    # value = variable to change
    # rhs = int to change it with
    def __init__(self, value : Node, rhs : int, line_nr: int, token_type = enums.token_types, node_type : enums.node_types=enums.node_types.MATH):
        super().__init__(value, line_nr, token_type, node_type)
        self.rhs = rhs
    
    def __str__(self) -> str:
        return '[{line_nr}] MathNode( {value}, {token_type} ,{rhs})'.format(
            line_nr = self.line_nr,
            value = self.value.__repr__(),
            token_type = self.token_type,
            rhs = self.rhs
        )
    def __repr__(self) -> str:
        return self.__str__()

    def visit(self) -> Node:
        visitor = Visitor()
        return visitor.visitMath(self)

class ConditionNode(Node):
    def __init__(self, value : Node, condition : Node, line_nr : int, token_type = enums.token_types, node_type: enums.node_types=enums.node_types.CONDITION):
        super().__init__(value, line_nr, token_type, node_type)
        self.condition = condition

    def __str__(self) -> str:
        return '({value} {token_type}, {condition})'.format(
            value = self.value.__repr__(),
            token_type = self.token_type,
            condition = self.condition.__repr__()
        )

    def __repr__(self) -> str:
        return self.__str__()

    def visit(self) -> Node:
        visitor = Visitor()
        return visitor.visitCondition(self)

class IfNode(Node):
    def __init__(self, value : Node, condition : ConditionNode, new_value : Node, line_nr : int, token_type = enums.token_types, node_type: enums.node_types=enums.node_types.IF):
        super().__init__(value, line_nr, token_type, node_type)
        self.condition = condition
        self.new_value = new_value
    
    def __str__(self) -> str:
        return '[{line_nr}] IfNode({value}, condition: {condition}, -> {new_value})'.format(
            line_nr = self.line_nr,
            value = self.value.__repr__(),
            condition = self.condition.__repr__(),
            new_value = self.new_value
        )

    def __repr__(self) -> str:
        return self.__str__()

    def visit(self) -> Node:
        visitor = Visitor()
        return visitor.visitIF(self)

#TODO fiks inheritance issue
def ErrorNode(Node): 
    def __init__(self, value : Node, line_nr : int, token_type : enums.token_types, node_type: enums.node_types=enums.node_types.ERROR):
        super().__init__(value, line_nr, token_type, node_type)

    def __str__(self) -> str:
        return "error(nr: {line_nr}, message: {value})".format(
            line_nr = self.line_nr,
            value = self.value.__repr__()
        )    

    def __repr__(self) ->str:
        return self.__str__()


#TODO visitor
dif_nodes = TypeVar(Node, VariableNode, MathNode, IfNode)
class FunctionNode(Node):
    # value = function name
    def __init__(self, value : Node, line_nr : int, commands: List[dif_nodes],input : List[Node], output : List[Node], variable_names: List[str], token_type : enums.token_types=enums.token_types.FUNCTION, node_type : enums.node_types.FUNCTION=enums.node_types.FUNCTION):
        super().__init__(value, line_nr, token_type, node_type)
        self.commands = commands
        self.input = input
        self.output = output
        self.variable_names = variable_names
    
    def __str__(self) -> str:
        return 'function: {value}, body: {commands}, input:{input}, output:{output}'.format(
            value = self.value,
            commands = self.commands,
            input = self.input,
            output = self.output
        )

    def __repr__(self) -> str:
        return self.__str__()

class Parser(object):
    def __init__(self):
        pass

    list_types = TypeVar(Node, VariableNode, MathNode)
    def parse(  self, token_list : List[lexer.Token], line_nr : int = 1, found_vars : List[VariableNode]=[], found_func_names : List[str]=[], 
                tree : List[list_types] = [], state :enums.parser_states=enums.parser_states.SINGLE) -> List[list_types]:

        if len( token_list ) == 0:
            return tree

        head, *tail = token_list

        value = head.value
        token_type = head.token_type
        if token_type == enums.token_types.FROM:
            found_line = [head] + self.getLine(tail)
            # based on length of line start assigning
            length_line = len(found_line)
            if found_line[0].token_type != enums.token_types.FROM and found_line[3].token_type != enums.token_types.TO:
                print("This print later throws an error, invalid syntax")
            if state == enums.parser_states.SINGLE:
                if length_line == 4:
                    #check for function decleration 
                    if found_line[3].token_type == enums.token_types.DECLARE:
                        check_var = self.findAndReturn(found_vars, found_line[1].value)
                        if len(check_var) == 0:
                            #goed er mag een functie worden gemaakt
                            found_func_names.append(found_line[1].value)
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, tree, state)
                        else:
                            print("functienaam is al variabele")
                    if found_line[1].token_type == enums.token_types.START:
                        if found_line[3].value in found_func_names:
                            function = FunctionNode(found_line[3].value, line_nr, [], [], [], [] , enums.token_types.FUNCTION)
                            tree.append(function) 
                            state = enums.parser_states.FUNCTION
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, tree, state)
                        else:
                            print("error function not declared")

                    elif found_line[3].token_type == enums.token_types.ERR:
                        var = ErrorNode(Node(found_line[1].value, line_nr, enums.token_types.STRING), line_nr, enums.token_types.ERR )
                        tree.append(var)
                        remaining_tail = tail[length_line-1:]
                        return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, tree, state)
                    #check for variable assignement
                    elif found_line[3].token_type == enums.token_types.VAR or found_line[3].token_type == enums.token_types.OUT:
                        var = self.getVarNode(found_line, found_vars, line_nr)

                        if found_line[3].token_type == enums.token_types.OUT:
                            var.token_type = enums.token_types.OUT
                        if var.token_type != enums.token_types.OUT:
                            found_vars.append(var)
                        tree.append(var)
                        remaining_tail = tail[length_line-1:]
                        return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, tree, state)
                    elif found_line[1].token_type == enums.token_types.IN:
                        temp = self.findAndReturn(found_vars, found_line[3].value)
                        if len(temp) == 1:
                            temp[0].value = enums.token_types.IN
                            tree.append(temp[0])
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, tree, state)
                        else:
                            var = VariableNode(found_line[3].value, found_line[1].value, line_nr, enums.token_types.VAR)
                            tree.append(var)
                            remaining_tail = tail[length_line-1:]

                elif length_line == 6:

                    # check for math
                    if found_line[1].token_type == enums.token_types.VAR and found_line[3].token_type == enums.token_types.VAR:
                        if (found_line[4].token_type is enums.token_types.ADD or
                            found_line[4].token_type is enums.token_types.MUL or
                            found_line[4].token_type is enums.token_types.SUB or
                            found_line[4].token_type is enums.token_types.DIV):

                                var = self.getMathNode(found_line, found_vars, line_nr)
                                tree.append(var)

                elif length_line == 7:
                    #check for if
                    if found_line[1].token_type == enums.token_types.VAR and found_line[5].token_type == enums.token_types.IF:
                        if (found_line[3].token_type == enums.token_types.EQUAL or
                            found_line[3].token_type == enums.token_types.NOTEQUAL or
                            found_line[3].token_type == enums.token_types.GREATER or
                            found_line[3].token_type == enums.token_types.SMALLER or
                            found_line[3].token_type == enums.token_types.EQUALGREATER or
                            found_line[3].token_type == enums.token_types.EQUALSMALLER):
                                    var = self.getIfNode(found_line, found_vars, line_nr)
                                    tree.append(var)
            elif state == enums.parser_states.FUNCTION:
                node = copy.copy(tree[-1])
                new_node = copy.copy(node)
                if node.node_type == enums.node_types.FUNCTION:
                    if length_line == 4:
                        # check for input assignement
                        if found_line[1].token_type == enums.token_types.INPUT:
                            temp = self.findAndReturn(node.variable_names, found_line[3])
                            if len(temp) == 0:
                                new_node.input.append(found_line[3].value)
                                remaining_tail = tail[length_line-1:]
                                return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, tree, state)
                            else:
                                print("error")
                        elif found_line[3].token_type == enums.token_types.OUTPUT:
                            temp = self.findAndReturn(new_node.variable_names, found_line[1])
                            if len(temp) == 0:
                                new_node.output.append(found_line[1].value)
                                remaining_tail = tail[length_line-1:]
                                return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, tree, state)
                            else:
                                print("error")
                        elif found_line[1].token_type == enums.token_types.END:
                            state = enums.parser_states.SINGLE
                            remaining_tail = tail[length_line-1:]
                            tree.pop(-1)
                            tree.append(new_node)
                            return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, tree, state)

                        # check for variable assignement
                        elif found_line[3].token_type == enums.token_types.VAR or found_line[3].token_type == enums.token_types.OUT:
                            var = self.getVarNode(found_line, new_node.variable_names, line_nr)

                            if found_line[3].token_type == enums.token_types.OUT:
                                var.token_type = enums.token_types.OUT
                            if var.token_type != enums.token_types.OUT:
                                new_node.variable_names.append(var)
                            new_node.commands.append(var)
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, tree, state)

                    elif length_line == 6:
                        # check for math
                        if found_line[1].token_type == enums.token_types.VAR and found_line[3].token_type == enums.token_types.VAR:
                            if (found_line[4].token_type is enums.token_types.ADD or
                                found_line[4].token_type is enums.token_types.MUL or
                                found_line[4].token_type is enums.token_types.SUB or
                                found_line[4].token_type is enums.token_types.DIV):

                                    var = self.getMathNode(found_line, new_node.variable_names, line_nr)
                                    node.commands.append(var)
                                    remaining_tail = tail[length_line-1:]
                                    return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, tree, state)
                    
                    elif length_line == 7:
                        #check for if
                        if found_line[1].token_type == enums.token_types.VAR and found_line[5].token_type == enums.token_types.IF:
                            if (found_line[3].token_type == enums.token_types.EQUAL or
                                found_line[3].token_type == enums.token_types.NOTEQUAL or
                                found_line[3].token_type == enums.token_types.GREATER or
                                found_line[3].token_type == enums.token_types.SMALLER or
                                found_line[3].token_type == enums.token_types.EQUALGREATER or
                                found_line[3].token_type == enums.token_types.EQUALSMALLER):
                                        var = self.getIfNode(found_line, new_node.variable_names, line_nr)
                                        node.commands.append(var)
                                        remaining_tail = tail[length_line-1:]
                                        return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, tree, state)

        remaining_tail = tail[length_line-1:]
        return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, tree, enums.parser_states.FUNCTION)

    def getVarNode(self, found_line : List[lexer.Token], found_vars : List[VariableNode], line_nr : int) -> VariableNode:
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
        return var

    def getMathNode(self, found_line : List[lexer.Token], found_vars : List[VariableNode], line_nr : int) -> MathNode:
        if found_line[1].value == found_line[3].value:
            if (found_line[5].token_type is enums.token_types.INT):
                var = self.findAndReturn(found_vars, found_line[1].value)
                nmbr = Node(found_line[5].value, line_nr, found_line[5].token_type, enums.node_types.BASE)
                if len(var) == 0:
                    print("Math on unknown variable")
                if len(var) == 1:
                    math = MathNode(var[0], nmbr, line_nr, found_line[4].token_type)
                    return math
            if (found_line[5].token_type is enums.token_types.VAR):
                var1 = self.findAndReturn(found_vars, found_line[1].value)
                var2 = self.findAndReturn(found_vars, found_line[5].value)
                if len(var1) == 0 or len(var2) == 0:
                    print("Math on unknown variable")
                if len(var1) == 1 and len(var2) == 1:
                    math = MathNode(var1[0], var2[0], line_nr, found_line[4].token_type)
                    return MathNode

    def getIfNode(self, found_line : List[lexer.Token], found_vars : List[VariableNode], line_nr : int):
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
        return var

    def getLine(self, tokens : List[lexer.Token], line : List[lexer.Token]=[]) -> List[lexer.Token]:
        
        if len(tokens) == 0:
            return []
        head, *tail = tokens 
        if head.token_type != enums.token_types.FROM:
            return [head] + self.getLine(tail)
        return []

    def findAndReturn(self,  search_area : List[VariableNode], value_to_find : str ) -> List[VariableNode]:
        if len(search_area) == 0:
            return []
        head, *tail = search_area
        if head.variable_name == value_to_find:
            return [copy.copy(head)]
        return [] + self.findAndReturn( tail, value_to_find)

class Visitor(object):
    def __init__(self):
        pass
    
    node_types = TypeVar(Node, VariableNode, MathNode, ConditionNode, IfNode)
    def visitAl(self, node_list : List[Node], copy_list :List[node_types]=[], state : str = "START") -> List[node_types]:
        if len(node_list) == 0:
            return copy_list
        if state == "START":
            head, *tail = node_list
            copy_list.append(head.visit())
            state == "MIDDLE"
        if state == "MIDDLE":
            head, *tail = node_list
            copy_list.append(head.visit())
        return self.visitAl(tail, copy_list, state)

    def visitNode(self, node : Node) -> lit_types:
        copy_node = copy.copy(node)
        return copy_node.value


    def visitVariable(self, node : VariableNode) -> VariableNode:
        copy_node = copy.copy(node)
        return copy_node

    #TODO math, if en condition zijn nu functioneel maar moeten nu anders behandeld worden, overkoepelende functie:
    def visitMath(self, node : MathNode) -> MathNode:
        copy_node = copy.copy(node)
        if copy_node.token_type == enums.token_types.ADD:
            function = lambda x, y:x+y
        elif copy_node.token_type == enums.token_types.SUB:
            function = lambda x, y: x-y
        elif copy_node.token_type == enums.token_types.MUL:
            function = lambda x, y: x*y
        elif copy_node.token_type == enums.token_types.DIV:
            function = lambda x, y: x//y
        
        if copy_node.rhs.token_type == enums.token_types.VAR:
            items = [copy_node.value.value.visit(), copy_node.rhs.value.visit()]
        else:
            items = [copy_node.value.value.visit(), copy_node.rhs.visit()]
        items = list(map(lambda x: int(x) if x.isnumeric() else x, items)) #HOGERE ORDE FUNCTIE
        copy_node.value.line_nr = node.line_nr
        copy_node.value.value = Node(functools.reduce(function, items), node.line_nr, enums.token_types.INT) #HOGERE ORDE FUNCTIE
        return copy_node

    def visitCondition(self, node : ConditionNode) -> bool:
        copy_node = copy.copy(node)
        if copy_node.token_type == enums.token_types.GREATER:
            function = lambda x,y: True if x > y else False
        elif copy_node.token_type == enums.token_types.SMALLER:
            function = lambda x,y: True if x < y else False
        elif copy_node.token_type == enums.token_types.EQUAL:
            function = lambda x,y: True if x == y else False
        elif copy_node.token_type == enums.token_types.EQUALGREATER:
            function = lambda x,y: True if x >= y else False
        elif copy_node.token_type == enums.token_types.EQUALSMALLER:
            function = lambda x,y: True if x <= y else False
        elif copy_node.token_type == enums.token_types.NOTEQUAL:
            function = lambda x,y: True if x != y else False

        items = [str(copy_node.value.value.visit()), str(copy_node.condition.visit())]
        if not items[0].isnumeric() and not items[1].isnumeric():
            if (copy_node.token_type == enums.token_types.EQUAL or
                copy_node.token_type == enums.token_types.NOTEQUAL):
                result = functools.reduce(function, items) #HOGERE ORDE FUNCTIE
                return result
        else:
            items = list(map(lambda x: int(x) if x.isnumeric() else x, items)) #HOGERE ORDE FUNCTIE
            result = functools.reduce(function, items) #HOGERE ORDE FUNCTIE
            return result

    def visitIF(self, node : IfNode) -> IfNode:
        copy_node = copy.copy(node)
        if copy_node.condition.visit() == True:
            copy_node.value.value = Node(node.new_value, node.line_nr, node.new_value.token_type)
        return copy_node