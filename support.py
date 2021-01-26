from typing import List, TypeVar, Union, Tuple, Callable
import functools
import operator
import copy

import enums

class Error(object):
    """Error class, inherits from object class"""    
    def __init__(self, message, line_nr):
        """__init__ for Error

        Args:
            message (str): Message to display with error
            line_nr (int): line number on which the error occurs
        """        
        self.message = message
        self.line_nr = line_nr

    def __str__(self) -> str:   
        return 'ERROR:{line_nr}: {message}'.format(
            message = self.message,
            line_nr = self.line_nr
        )

    def __repr__(self) -> str:    
        return self.__str__()

# base node / literal node
lit_types = TypeVar('lit_types', int, str)
class Node(object):
    """Node class, inherits from object"""    
    def __init__(self, value : lit_types, line_nr: int,token_type : enums.token_types, node_type : enums.node_types=enums.node_types.BASE):
        """__init__ for Node

        Args:
            value (lit_types): Value that the Node holds
            line_nr (int): Linenumber where Node is created
            token_type (enums.token_types): token type of node
            node_type (enums.node_types, optional): node type. Defaults to enums.node_types.BASE.
        """        
        self.value = value
        self.token_type = token_type
        self.node_type = node_type
        self.line_nr = line_nr
    def __str__(self): 
        return 'Node({value})'.format(
            value=self.value
        )

    def __repr__(self) -> str:
        return self.__str__()

    # visit :: dict, dict -> lit_types
    def visit(self, variables : dict, found_funcs : dict = {} ) -> lit_types:
        visitor = Visitor()
        return visitor.visitNode(self, variables, found_funcs)

variable_values = TypeVar(Node)
class VariableNode(Node):
    """VariableNode class, inherits from Node"""    
    def __init__(self, variable_name : str, value : variable_values, line_nr: int, token_type , node_type : enums.node_types=enums.node_types.VAR):
        """__init__ for VariableNode

        Args:
            variable_name (str): name of the variable
            value (variable_values): value of the variable
            line_nr (int): line number of creation
            token_type ([type]): token type of value
            node_type (enums.node_types, optional): node type. Defaults to enums.node_types.VAR.
        """        
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

    # visit :: dict, dict -> lit_types
    def visit(self,variables : dict, found_funcs : dict = {} ) -> Node:
        visitor = Visitor()
        return visitor.visitVariable(self, variables, found_funcs)

class MathNode(Node):
    """MathNode class, inherits from Node class
    """    
    def __init__(self, value : Node, rhs : Node, line_nr: int, token_type = enums.token_types, node_type : enums.node_types=enums.node_types.MATH):
        """__init__ for MathNode

        Args:
            value (Node): lhs, variable to be changed
            rhs (Node): rhs
            line_nr (int): line number of MathNode
            token_type ([type], optional): token_type, defines the type of operator. Defaults to enums.token_types.
            node_type (enums.node_types, optional): node type. Defaults to enums.node_types.MATH.
        """        
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

    # visit :: dict, dict -> lit_types
    def visit(self, variables : dict , found_funcs : dict = {}) -> Node:
        visitor = Visitor()
        return visitor.visitMath(self, variables, found_funcs)

class ConditionNode(Node):
    """ConditionNode class, inherits from Node
    """    
    def __init__(self, value : Node, condition : Node, line_nr : int, token_type = enums.token_types, node_type: enums.node_types=enums.node_types.CONDITION):
        """__init__ for conditionNode

        Args:
            value (Node): lhs
            condition (Node): rhs
            line_nr (int): linenumber of condition
            token_type ([type], optional): token type . Defaults to enums.token_types.
            node_type (enums.node_types, optional): node type. Defaults to enums.node_types.CONDITION.
        """        
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

    # visit :: dict, dict -> lit_types
    def visit(self, variables: dict, found_funcs : dict = {} ) -> Node:
        visitor = Visitor()
        return visitor.visitCondition(self, variables, found_funcs)

class IfNode(Node):
    """IfNode class, inherits from Node
    """    
    def __init__(self, value : Node, condition : ConditionNode, new_value_true : Node, new_value_false : Node, line_nr : int, token_type = enums.token_types, node_type: enums.node_types=enums.node_types.IF):
        """__init__ for IfNode

        Args:
            value (Node): variable to if on
            condition (ConditionNode): condition -> true or false
            new_value (Node): new value for value if condition is true
            line_nr (int): line number of if statement
            token_type ([type], optional): token type. Defaults to enums.token_types.
            node_type (enums.node_types, optional): node type. Defaults to enums.node_types.IF.
        """        
        super().__init__(value, line_nr, token_type, node_type)
        self.condition = condition
        self.new_value_true = new_value_true
        self.new_value_false = new_value_false
    
    def __str__(self) -> str:
        return '[{line_nr}] IfNode({value}, condition: {condition}, -> {new_value_true} OR {new_value_false})'.format(
            line_nr = self.line_nr,
            value = self.value.__repr__(),
            condition = self.condition.__repr__(),
            new_value_true = self.new_value_true,
            new_value_false = self.new_value_false
        )

    def __repr__(self) -> str:
        return self.__str__()

    # visit :: dict, dict -> lit_types
    def visit(self, variables : dict , found_funcs : dict = {}) -> Node:
        visitor = Visitor()
        return visitor.visitIF(self, variables, found_funcs)


dif_nodes = TypeVar(Node, MathNode, IfNode, VariableNode)
class FunctionNode(Node):
    """FunctionNode class, inherits from Node"""    
    def __init__(self, value : Node, line_nr : int, commands: List[dif_nodes]=[], variables: List[VariableNode]=[], token_type : enums.token_types=enums.token_types.FUNCTION, node_type : enums.node_types.FUNCTION=enums.node_types.FUNCTION):
        """__init__ for FunctionNode

        Args:
            value (Node): name of function
            line_nr (int): linenumber of function decleration, not realy used
            commands (List[dif_nodes]): list of nodes containing the body of the function
            input (List[Node]): input when called by user
            output (List[Node]): output when called by user
            variables (List[VariableNode]): used variables in function
            token_type (enums.token_types, optional): token type. Defaults to enums.token_types.FUNCTION.
            node_type (enums.node_types.FUNCTION, optional): node type. Defaults to enums.node_types.FUNCTION.
        """        
        super().__init__(value, line_nr, token_type, node_type)
        self.commands = commands
        self.variables = variables
    
    def __str__(self) -> str:
        return '{value}\n body: ({commands})'.format(
            value = self.value,
            commands = self.commands,
        )

    def __repr__(self) -> str:
        return self.__str__()

    # visit :: dict, dict -> lit_types
    def visit(self, input : Node, variables : dict , found_funcs : dict = {}):
        visitor = Visitor()
        return visitor.visitFunction(self, input, variables, found_funcs)

class FunctionCall(Node):
    """FunctionCall class, inherits from Node""" 
    def __init__(self, value : Node, line_nr : int, input : Node, output : VariableNode, token_type : enums.token_types, node_type : enums.node_types= enums.node_types.FUNCTION_CALL):
        """__init__ for functionCall node

        Args:
            value (Node): functionNode that holds the function
            line_nr (int): line number of function call
            input (Node): input to be put into function
            output (VariableNode): outputVariable to store function result into
            token_type (enums.token_types): token type of node
            node_type (enums.node_types, optional): node type of node. Defaults to enums.node_types.FUNCTION_CALL.
        """
        super().__init__(value, line_nr, token_type, node_type)
        self.input = input
        self.output = output

    def __str__(self) -> str:
        return '{output_value}={function}({input})'.format(
            output_value = self.output.variable_name,
            function = self.value,
            input = self.input
        )

    def __repr__(self) -> str:
        return self.__str__()

    # visit :: dict, dict -> lit_types
    def visit(self, variables : dict, found_funcs : dict = {}):
        visitor = Visitor()
        return visitor.visitFunctionCall(self, variables, found_funcs)

def smart_divide(func : Callable[[int,int], int]):
    def inner_divide(lhs,rhs):
        if lhs == 0:
            return 0
        elif rhs == 0:
            return 0
        else:
            return func( lhs,rhs)
    return inner_divide
@smart_divide
def divide(lhs : int, rhs: int):
    return lhs / rhs

class Visitor(object):
    def __init__(self):
        pass
    
    node_types = TypeVar(Node, VariableNode, MathNode, ConditionNode, IfNode)
    # visitAl :: List[Node], List[Node], dict, dict -> Union(Error,dict)
    def visitAl(self, node_list : List[Node], node_list_copy : List[Node], variables : dict={}, found_funcs : dict = {}) -> Union[Error,dict]:

        if len(node_list) == 0:
            return variables
        head, *tail = node_list
        variables_copy = copy.copy(variables)

        if head.token_type == enums.token_types.LINE:
            start_line, variables_copy = head.visit(variables_copy, found_funcs)
            if type(start_line) is Error:
                return start_line
            if start_line is Node:
                start_line, variables_copy = start_line.visit(variables_copy, found_funcs)
            start_line = str(start_line)
            if not start_line.isnumeric():
                just_number = start_line.lstrip("-")
                if just_number.isnumeric():
                    start_line = int(start_line)
                else:
                    error = Error("Line number to jump to not int", head.line_nr)
                    return error
            if int(start_line) >= 0:
                if int(start_line) <= len(tail):
                    start_line = int(start_line) - 1
                    tail = copy.copy(tail[int(start_line):])
                elif int(start_line)-1 == 0:
                    tail = copy.copy(tail[1:])
                else:
                    tail= []
                return self.visitAl(tail, node_list_copy, variables_copy, found_funcs)
            else:
                current_index = len(node_list_copy)-len(node_list)
                tail = node_list_copy[current_index + start_line:]
        else:
            pos_error, variables_copy = head.visit(variables_copy, found_funcs)
            if type(pos_error) is Error:
                return pos_error
        return self.visitAl(tail, node_list_copy, variables_copy, found_funcs)
        
    # visitNode :: Node, dict, dict -> Tuple[Union[Error,lit_types], dict]
    def visitNode(self, node : Node, variables: dict , found_funcs : dict = {} ) -> Tuple[Union[Error,lit_types], dict]:
        copy_node = copy.copy(node)
        return copy_node.value, variables

    # visitVariable :: Node, dict, dict -> Tuple[Union[Error,node_types], dict]
    def visitVariable(self, node : Node, variables: dict , found_funcs : dict = {} ) -> Tuple[Union[Error,node_types], dict]:
        copy_node = copy.copy(node)
        variables_copy = copy.deepcopy(variables)

        if copy_node.token_type == enums.token_types.VAR or copy_node.token_type == enums.token_types.OUTPUT:
            if copy_node.value.value == "INPUT":
                input_node = variables_copy["INPUT"]
                variables_copy[copy_node.variable_name] = input_node
                input_node, variables_copy = input_node.visit( variables_copy, found_funcs)
                return input_node, variables_copy

            elif copy_node.value.token_type == enums.token_types.VAR:
                node_value = variables_copy[copy_node.value.variable_name]
                variables_copy[copy_node.variable_name] = node_value
                node_value, variables_copy = node_value.visit( variables_copy, found_funcs)
                return node_value, variables_copy

            elif copy_node.value.token_type == enums.token_types.INPUT:
                input_value = variables_copy["INPUT"]
                new_node = Node(input_value, copy_node.line_nr, enums.token_types.STRING)
                variables_copy[copy_node.variable_name] = new_node
                return input_value, variables_copy
            else: #literals
                if copy_node.variable_name in variables_copy:
                    value = variables_copy[copy_node.variable_name]
                else:
                    value = copy_node.value
                variables_copy[copy_node.variable_name] = value
                return value, variables_copy

        elif copy_node.token_type == enums.token_types.OUT:
            if copy_node.value.token_type == enums.token_types.VAR:
                printable = variables_copy[copy_node.value.variable_name]
                printable, variables_copy = printable.visit(variables_copy, found_funcs)
                if type(printable) is Error:
                    return printable, variables_copy
            else:
                printable, variables_copy = copy_node.value.visit(variables_copy, found_funcs)
                if type(printable) is Error:
                    return printable, variables_copy
            print(printable)
            return printable, variables_copy

        elif copy_node.token_type == enums.token_types.LINE:
            if copy_node.value.token_type == enums.token_types.VAR:
                node_value = variables_copy[copy_node.value.variable_name]
                line_number, variables_copy = node_value.visit(variables_copy, found_funcs)
                if type(line_number) is VariableNode:
                    if line_number.token_type == enums.token_types.VAR:
                        line_number, variables_copy = line_number.value.visit(variables_copy, found_funcs)
            else:
                line_number, variables_copy = copy_node.value.visit(variables_copy, found_funcs)
            return line_number, variables_copy # returned echte ints, geen nodes

        elif copy_node.token_type == enums.token_types.ERR:
            error = Error(copy_node.value, copy_node.line_nr)
            return error, variables_copy

        elif copy_node.token_type == enums.token_types.DECLARE:
            return copy_node, variables_copy


    # visitMath :: Node, dict, dict -> Tuple[Union[Error,int], dict]
    def visitMath(self, node : MathNode, variables: dict , found_funcs : dict = {}) -> Tuple[Union[Error,int], dict]:
        copy_node = copy.copy(node)
        variables_copy = copy.copy(variables)
        if copy_node.token_type == enums.token_types.ADD:
            function = lambda x, y:x+y
        elif copy_node.token_type == enums.token_types.SUB:
            function = lambda x, y: x-y
        elif copy_node.token_type == enums.token_types.MUL:
            function = lambda x, y: x*y
        elif copy_node.token_type == enums.token_types.DIV:
            function = lambda x, y: divide(x,y) # DECORATED
        else:
            error = Error("unknown operator in Math statement", copy_node.line_nr)
            return error, variables_copy

        if copy_node.rhs.token_type == enums.token_types.VAR:
            item_2 = variables_copy[copy_node.rhs.variable_name]
            item_2, variables_copy = item_2.visit(variables_copy, found_funcs)
        else:
            item_2, variables_copy = copy_node.rhs.visit(variables_copy, found_funcs)
        
        if copy_node.value.token_type == enums.token_types.VAR:
            item_1 = variables_copy[copy_node.value.variable_name]
            item_1, variables_copy = item_1.visit(variables_copy, found_funcs)
        else: 
            item_1, variables_copy = copy_node.value.visit(variables_copy, found_funcs)

        items = [str(item_1), str(item_2)]
        if items[0].isnumeric():
            items[0] = int(items[0])
        if items[1].isnumeric():
            items[1] = int(items[1])
        if type(items[0]) == str:
            if "-" in items[0]:
                just_number = items[0].lstrip("-")
                if just_number.isnumeric():
                    items[0] = int("-" + just_number)
        if type(items[1]) == str:
            if "-" in items[1]:
                just_number2 = items[1].lstrip("-")
                if just_number2.isnumeric():
                    items[1] = int("-" + just_number2)

        new_value = Node(functools.reduce(function, items), node.line_nr, enums.token_types.INT) #HOGERE ORDE FUNCTIE
        if copy_node.value.variable_name in variables_copy:
            variables_copy[copy_node.value.variable_name] = new_value
            return new_value, variables_copy
        else:
            error = Error("Math statement on unknown variable", copy_node.line_nr)
            return error, variables_copy
    # visitCondition :: Node, dict, dict -> Tuple[Union[Error,bool], dict]
    def visitCondition(self, node : ConditionNode, variables: dict , found_funcs : dict = {}) -> Tuple[Union[Error, bool], dict]:
        copy_node = copy.copy(node)
        variables_copy = copy.copy(variables)
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
        else:
            error = Error("unknown operator in condition statement", copy_node.line_nr)
            return error, variables_copy

        if copy_node.value.token_type == enums.token_types.VAR:
            item_1 = variables_copy[copy_node.value.variable_name]
            item_1, variables_copy = item_1.visit(variables_copy, found_funcs)
        else:
            item_1, variables_copy = copy_node.value.visit(variables_copy, found_funcs)
        
        if copy_node.condition.token_type == enums.token_types.VAR:
            item_2 = variables_copy[copy_node.condition.variable_name]
            item_2, variables_copy = item_2.visit(variables_copy, found_funcs)
        else: 
            item_2, variables_copy = copy_node.condition.visit(variables_copy, found_funcs)

        items = [str(item_1), str(item_2)]
        if items[0].isnumeric():
            items[0] = int(items[0])
        if items[1].isnumeric():
            items[1] = int(items[1])
        if type(items[0]) == str:
            if "-" in items[0]:
                just_number = items[0].lstrip("-")
                if just_number.isnumeric():
                    items[0] = int("-" + just_number)
        if type(items[1]) == str:
            if "-" in items[1]:
                just_number2 = items[1].lstrip("-")
                if just_number2.isnumeric():
                    items[1] = int("-" + just_number2)

        if type(items[0]) == str and type(items[1]) == str:
            if (copy_node.token_type == enums.token_types.EQUAL or
                copy_node.token_type == enums.token_types.NOTEQUAL):
                result = functools.reduce(function, items) #HOGERE ORDE FUNCTIE
                return result, variables_copy
            else:
                error = Error("cant use operator on string variables", copy_node.line_nr)
                return Error, variables_copy
        elif type(items[0]) == int and type(items[1]) == int:
            result = functools.reduce(function, items) #HOGERE ORDE FUNCTIE
            return result, variables_copy
        else:
            error = Error("cant compare variables of different type", copy_node.line_nr)
            return error, variables_copy

    # visitIF :: Node, dict, dict -> Tuple[Union[Error,lit_types], dict]
    def visitIF(self, node : IfNode, variables: dict , found_funcs : dict = {}) -> Tuple[Union[Error,lit_types], dict]:
        variables_copy = copy.copy(variables)
        copy_node = copy.copy(node)
        result, variables_copy = copy_node.condition.visit(variables_copy, found_funcs)
        if result is Error:
            return result, variables_copy
        if result == True:
            if copy_node.value.variable_name in variables_copy:
                variables_copy[copy_node.value.variable_name] = copy_node.new_value_true
                return copy_node.new_value_true, variables_copy 
            else:
                error = Error("if statement on undeclared variable", copy_node.line_nr)
                return error, variables_copy  
        else:
            if copy_node.new_value_false is not None:
                if copy_node.value.variable_name in variables_copy:
                    variables_copy[copy_node.value.variable_name] = copy_node.new_value_false
                    return copy_node.new_value_false, variables_copy 
                else:
                    error = Error("if statement on undeclared variable", copy_node.line_nr)
                    return error, variables_copy  
        return copy_node.value, variables_copy

    # visitFunctionCall :: Node, dict, dict -> Tuple[Union[Error,VariableNode], dict]
    def visitFunctionCall(self, node : FunctionNode, variables: dict , found_funcs : dict = {}) -> Tuple[Union[Error, VariableNode], dict]:
        variables_copy = copy.copy(variables)
        copy_node = copy.copy(node)

        function = found_funcs[copy_node.value]
        function_output, variables_copy = function.visit(copy_node.input, variables_copy, found_funcs)
        copy_node.output.value = function_output
        variables_copy[copy_node.output.variable_name] = copy_node.output.value
        return function_output, variables_copy

    # visitFunction :: Node, dict, dict -> Tuple[Union[Error,VariableNode], dict]
    def visitFunction(self, node : FunctionNode, input : Node, variables: dict , found_funcs : dict = {}) -> Tuple[Union[Error, VariableNode], dict]:
        variables_copy = copy.copy(variables)
        copy_node = copy.copy(node)
        copy_input = copy.copy(input)
        function_variables = {}

        if copy_input.token_type == enums.token_types.VAR:
            copy_input = variables[copy_input.variable_name]
            input_value = copy_input
        else:
            input_value = copy_input
        input_node = VariableNode("INPUT", input_value, copy_node.line_nr, enums.token_types.VAR, enums.node_types.VAR)
        copy_node.commands = [input_node] + copy_node.commands

        new_function_variables = self.visitAl(copy_node.commands, copy_node.commands, function_variables, found_funcs)
        
        if type(new_function_variables) is Error:
            return new_function_variables, variables_copy

        if 'OUTPUT' in new_function_variables:
            result = new_function_variables["OUTPUT"]
            return result, variables_copy
        else:
            error = Error("No output specified in function", copy_node.line_nr)
            return error, variables_copy