from typing import List, TypeVar, Union
import functools
import operator
import copy

import enums
import lexer

#TODO GOTO statements, error handling

# base node / literal node
lit_types = TypeVar('lit_types', int, str)
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

variable_values = TypeVar(Node)
class VariableNode(Node):
    def __init__(self, variable_name : str, value : variable_values, line_nr: int, token_type , node_type : enums.node_types=enums.node_types.VAR):
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

# class GoToNode(Node):
    

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


#TODO visitor
dif_nodes = TypeVar(Node, MathNode, IfNode, VariableNode)
class FunctionNode(Node):
    # value = function name
    def __init__(self, value : Node, line_nr : int, commands: List[dif_nodes],input : List[Node], output : List[Node], variables: List[VariableNode], token_type : enums.token_types=enums.token_types.FUNCTION, node_type : enums.node_types.FUNCTION=enums.node_types.FUNCTION):
        super().__init__(value, line_nr, token_type, node_type)
        self.commands = commands
        self.input = input
        self.output = output
        self.variables = variables
    
    def __str__(self) -> str:
        return ' function[ {value}, body: ({commands}), \n input:{input}, \n output:{output} ]'.format(
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
                found_funcs : List[FunctionNode]=[], tree : List[list_types] = [], state :enums.parser_states=enums.parser_states.SINGLE, function_line_nr : int = 1) -> List[list_types]:

        found_vars = copy.copy(found_vars)
        found_func_names = copy.copy(found_func_names)
        found_funcs = copy.copy(found_funcs)
        tree = copy.copy(tree)

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
                        check_var = self.findAndReturnVar(found_vars, found_line[1].value)
                        if check_var == False:
                            #goed er mag een functie worden gemaakt
                            #TODO voeg declare toe aan tree zodat goto statements een voleldige boom krijgen
                            found_func_names.append(found_line[1].value)
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, found_funcs, tree, state)
                        else:
                            print("functienaam is al variabele")
                    if found_line[1].token_type == enums.token_types.START:
                        if found_line[3].value in found_func_names:
                            function = FunctionNode(found_line[3].value, line_nr, [], [], [], [] , enums.token_types.FUNCTION)
                            tree.append(function) 
                            state = enums.parser_states.FUNCTION
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, found_funcs, tree, state)
                        else:
                            print("error function not declared")

                    #check for variable assignement
                    elif found_line[3].token_type == enums.token_types.VAR or found_line[3].token_type == enums.token_types.OUT:
                        var = self.getVarNode(found_line, found_vars, line_nr)

                        if found_line[3].token_type == enums.token_types.OUT:
                            var.token_type = enums.token_types.OUT
                        if var.token_type != enums.token_types.OUT:
                            found_vars.append(var)
                        tree.append(var)
                        remaining_tail = tail[length_line-1:]
                        return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, found_funcs, tree, state)

                elif length_line == 6:
                    #check for function call
                    if found_line[1].value in found_func_names:
                        var = self.findAndReturnFunc(found_funcs, found_line[1].value)
                        if var is not False:
                            func = copy.copy(var)
                            input_node = temp_var = VariableNode(found_line[3].value, Node(found_line[1].value, function_line_nr, found_line[1].token_type), function_line_nr, found_line[1].token_type)
                            func.input.append(input_node)
                            func.output.append(VariableNode(found_line[5].value, Node(None, line_nr, None), line_nr, enums.token_types.VAR))
                            var = VariableNode(found_line[5].value, func, line_nr, enums.token_types.FUNCTION)
                            tree.append(var)
                            found_vars.append(var)
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, found_funcs, tree, state)
                        else:
                            print("error")

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
                            temp = self.findAndReturnVar(node.variables, found_line[3])
                            if temp == False:
                                temp_var = VariableNode(found_line[3].value, Node(found_line[1].value, function_line_nr, enums.token_types.INPUT), function_line_nr, enums.token_types.VAR, enums.node_types.INPUT)
                                new_node.commands.append(temp_var)
                                new_node.variables.append(temp_var)
                                new_node.input.append(temp_var)
                                remaining_tail = tail[length_line-1:]
                                return self.parse(remaining_tail, line_nr, found_vars, found_func_names, found_funcs,tree, state, function_line_nr+1)
                            else:
                                print("error")
                        elif found_line[3].token_type == enums.token_types.OUTPUT:
                            temp = self.findAndReturnVar(new_node.variables, found_line[1])
                            if temp == False:
                                temp_var = VariableNode(found_line[3].value, Node(found_line[1].value, function_line_nr, found_line[1].token_type), function_line_nr, found_line[1].token_type)
                            else:
                                temp_var = VariableNode(found_line[3].value, temp, function_line_nr, found_line[1].token_type)
                            new_node.commands.append(temp_var)
                            new_node.output.append(temp_var)
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr, found_vars, found_func_names, found_funcs,tree, state, function_line_nr+1)
                        elif found_line[1].token_type == enums.token_types.END:
                            state = enums.parser_states.SINGLE
                            remaining_tail = tail[length_line-1:]
                            tree.pop(-1)
                            found_funcs.append(new_node)
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, found_funcs,tree, state, function_line_nr+1)

                        # check for variable assignement
                        elif found_line[3].token_type == enums.token_types.VAR or found_line[3].token_type == enums.token_types.OUT:
                            var = self.getVarNode(found_line, new_node.variables, function_line_nr)

                            if found_line[3].token_type == enums.token_types.OUT:
                                var.token_type = enums.token_types.OUT
                            if var.token_type != enums.token_types.OUT:
                                new_node.variables.append(var)
                            new_node.commands.append(var)
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr, found_vars, found_func_names, found_funcs,tree, state, function_line_nr+1)

                    elif length_line == 6:
                        # check for math
                        if found_line[1].token_type == enums.token_types.VAR and found_line[3].token_type == enums.token_types.VAR:
                            if (found_line[4].token_type is enums.token_types.ADD or
                                found_line[4].token_type is enums.token_types.MUL or
                                found_line[4].token_type is enums.token_types.SUB or
                                found_line[4].token_type is enums.token_types.DIV):

                                    var = self.getMathNode(found_line, new_node.variables, line_nr)
                                    node.commands.append(var)
                                    remaining_tail = tail[length_line-1:]
                                    return self.parse(remaining_tail, line_nr, found_vars, found_func_names, found_funcs,tree, state, function_line_nr+1)
                    
                    elif length_line == 7:
                        #check for if
                        if found_line[1].token_type == enums.token_types.VAR and found_line[5].token_type == enums.token_types.IF:
                            if (found_line[3].token_type == enums.token_types.EQUAL or
                                found_line[3].token_type == enums.token_types.NOTEQUAL or
                                found_line[3].token_type == enums.token_types.GREATER or
                                found_line[3].token_type == enums.token_types.SMALLER or
                                found_line[3].token_type == enums.token_types.EQUALGREATER or
                                found_line[3].token_type == enums.token_types.EQUALSMALLER):
                                        var = self.getIfNode(found_line, new_node.variables, line_nr)
                                        node.commands.append(var)
                                        remaining_tail = tail[length_line-1:]
                                        return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, found_funcs,tree, state, function_line_nr+1)

        remaining_tail = tail[length_line-1:]
        return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, found_funcs, tree, enums.parser_states.FUNCTION)

    def getVarNode(self, found_line : List[lexer.Token], found_vars : List[VariableNode], line_nr : int) -> VariableNode:
        # check if y var already exists
        check_exist_y = self.findAndReturnVar(found_vars, found_line[3].value)
        if check_exist_y == False:
            #variable does not exist yet
            #check if var x already exists
            if found_line[1].token_type == enums.token_types.VAR:
                check_exist_x = self.findAndReturnVar(found_vars, found_line[1].value)
                if check_exist_x is not False:
                    var = VariableNode(found_line[3].value, check_exist_x, line_nr, enums.token_types.VAR)
                else:
                    print("1 error trying to assign var that does not exist, or double var")
            elif found_line[1].token_type == enums.token_types.INT:
                var = VariableNode(found_line[3].value, Node(found_line[1].value, line_nr, enums.token_types.INT), line_nr, enums.token_types.VAR)
            elif found_line[1].token_type == enums.token_types.STRING:
                var = VariableNode(found_line[3].value, Node(found_line[1].value, line_nr, enums.token_types.STRING), line_nr, enums.token_types.VAR)
        elif len(check_exist_y) == 1:
            #variable does exist
            #check if var x already exists
            if found_line[1].token_type == enums.token_types.VAR:
                check_exist_x = self.findAndReturnVar(found_vars, found_line[1].value)
                if check_exist_x is not False:
                    check_exist_y.value = check_exist_x
                    check_exist_y.line_nr = line_nr
                    var = check_exist_y
                else:
                    print("2 error trying to assign var that does not exist, or double var")
            elif found_line[1].token_type == enums.token_types.INT:
                check_exist_y.value = Node(found_line[1].value, line_nr, enums.token_types.INT)
                check_exist_y.line_nr = line_nr
                var = check_exist_y
            elif found_line[1].token_type == enums.token_types.STRING:
                check_exist_y.value = Node(found_line[1].value, line_nr, enums.token_types.STRING)
                check_exist_y.line_nr = line_nr
                var = check_exist_y
        else:
            print("hier komt ene error")
        return var

    def getMathNode(self, found_line : List[lexer.Token], found_vars : List[VariableNode], line_nr : int) -> MathNode:
        if found_line[1].value == found_line[3].value:
            if (found_line[5].token_type is enums.token_types.INT):
                var = self.findAndReturnVar(found_vars, found_line[1].value)
                nmbr = Node(found_line[5].value, line_nr, found_line[5].token_type, enums.node_types.BASE)
                if var == False:
                    print("Math on unknown variable")
                else:
                    math = MathNode(var, nmbr, line_nr, found_line[4].token_type)
                    return math
            if (found_line[5].token_type is enums.token_types.VAR):
                var1 = self.findAndReturnVar(found_vars, found_line[1].value)
                var2 = self.findAndReturnVar(found_vars, found_line[5].value)
                if var1 == False or var2 == False:
                    print("Math on unknown variable")
                if var1 is not False and var2 is not False:
                    math = MathNode(var1, var2, line_nr, found_line[4].token_type)
                    return MathNode

    def getIfNode(self, found_line : List[lexer.Token], found_vars : List[VariableNode], line_nr : int):
        check_exist_value = self.findAndReturnVar(found_vars, found_line[1].value)
        if check_exist_value == False:
            print("value to if on does not exist")
        else:
            if found_line[4].token_type == enums.token_types.VAR:
                check_exist_condition = self.findAndReturnVar(found_vars, found_line[4].value)
                if check_exist_condition is False:
                    print("error condition does not exist")
                else:
                    condition = ConditionNode(check_exist_value, check_exist_condition, line_nr, found_line[3].token_type)
            elif found_line[4].token_type == enums.token_types.INT:
                condition = ConditionNode(check_exist_value, Node(found_line[4].value, line_nr, enums.token_types.INT), line_nr, found_line[3].token_type)
            elif found_line[4].token_type == enums.token_types.STRING:
                condition = ConditionNode(check_exist_value, Node(found_line[4].value, line_nr, enums.token_types.STRING), line_nr, found_line[3].token_type)

            if found_line[6].token_type == enums.token_types.VAR:
                check_exist_new_value = self.findAndReturnVar(found_vars, found_line[6].value)
                if check_exist_new_value is False:
                    print("error new value does not exist")
                else:
                    new_value = check_exist_new_value
            elif found_line[6].token_type == enums.token_types.INT:
                new_value = Node(found_line[6].value, line_nr, enums.token_types.INT)
            elif found_line[6].token_type == enums.token_types.STRING:
                new_value = Node(found_line[6].value, line_nr, enums.token_types.STRING)
            
            var = IfNode(check_exist_value, condition, new_value, line_nr, enums.token_types.IF)
        return var

    def getLine(self, tokens : List[lexer.Token], line : List[lexer.Token]=[]) -> List[lexer.Token]:
        
        if len(tokens) == 0:
            return []
        head, *tail = tokens 
        if head.token_type != enums.token_types.FROM:
            return [head] + self.getLine(tail)
        return []

    def findAndReturnVar(self,  search_area : List[VariableNode], value_to_find : str ) -> Union[VariableNode, bool]:
        if not search_area:
            return False
        head, *tail = search_area
        if head.variable_name == value_to_find:
            return copy.copy(head)
        return self.findAndReturnVar( tail, value_to_find)

    def findAndReturnFunc(self,  search_area : List[FunctionNode], value_to_find : str ) -> Union[FunctionNode,bool]:
        if not search_area:
            return False
        head, *tail = search_area
        if head.value == value_to_find:
            return copy.copy(head)
        return self.findAndReturnFunc( tail, value_to_find)







class Visitor(object):
    def __init__(self):
        pass
    
    node_types = TypeVar(Node, VariableNode, MathNode, ConditionNode, IfNode)
    def visitAl(self, node_list : List[Node], copy_list :List[node_types]=[]) -> List[node_types]:
        if len(node_list) == 0:
            return copy_list
        head, *tail = node_list
        copy_list.append(head.visit())
        return self.visitAl(tail, copy_list)

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