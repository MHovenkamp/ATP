from typing import List, TypeVar, Union, Tuple
import functools
import operator
import copy

import enums
import lexer


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

    def visit(self,variables : dict, found_funcs : dict = {} ) -> Node:
        visitor = Visitor()
        return visitor.visitVariable(self, variables, found_funcs)

class MathNode(Node):
    """MathNode class, inherits from Node class
    """    
    def __init__(self, value : Node, rhs : int, line_nr: int, token_type = enums.token_types, node_type : enums.node_types=enums.node_types.MATH):
        """__init__ for MathNode

        Args:
            value (Node): lhs, variable to be changed
            rhs (int): rhs
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

    def visit(self, variables : dict , found_funcs : dict = {}) -> Node:
        visitor = Visitor()
        return visitor.visitIF(self, variables, found_funcs)


dif_nodes = TypeVar(Node, MathNode, IfNode, VariableNode)
class FunctionNode(Node):
    """FunctionNode class, inherits from Node"""    
    # value = function name
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

    def visit(self, input : Node, variables : dict , found_funcs : dict = {}):
        visitor = Visitor()
        return visitor.visitFunction(self, input, variables, found_funcs)

class FunctionCall(Node):
    def __init__(self, value : Node, line_nr : int, input : Node, output : VariableNode, token_type : enums.token_types, node_type : enums.node_types= enums.node_types.FUNCTION_CALL):
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

    def visit(self, variables : dict, found_funcs : dict = {}):
        visitor = Visitor()
        return visitor.visitFunctionCall(self, variables, found_funcs)

class Parser(object):
    def __init__(self):
        pass

    list_types = TypeVar(Node, VariableNode, MathNode, Error)
    def parse(  self, token_list : List[lexer.Token], line_nr : int = 1, found_vars : List[VariableNode]=[],
                found_funcs : dict = {}, tree : List[list_types] = [], state :enums.parser_states=enums.parser_states.SINGLE, function_line_nr : int = 1, errors : List[Error]=[]) -> Tuple[List[list_types], dict]:
        """parser function

        Args:
            token_list (List[lexer.Token]): list of tokens
            line_nr (int, optional): linenumber of current found line. Defaults to 1.
            found_vars (List[VariableNode], optional): found variables in code. Defaults to [].
            found_funcs (List[FunctionNode], optional): found function list in code. Defaults to [].
            tree (List[list_types], optional): AST. Defaults to [].
            state (enums.parser_states, optional):current state. Defaults to enums.parser_states.SINGLE.
            function_line_nr (int, optional): line number within possible function. Defaults to 1.
            errors (List[Error], optional): list of found errors. Defaults to [].

        Returns:
            List[list_types]: [description]
        """        
        found_vars = copy.copy(found_vars)
        found_funcs = copy.copy(found_funcs)
        errors = copy.copy(errors)
        tree = copy.copy(tree)

        if len( errors ) > 0:
            return errors, found_funcs

        if len( token_list ) == 0:
            return tree, found_funcs

        head, *tail = token_list

        value = head.value
        token_type = head.token_type
        if token_type == enums.token_types.FROM:
            found_line = [head] + self.getLine(tail)

            # based on length of line start assigning
            length_line = len(found_line)
            if len(found_line) != 6:
                if found_line[0].token_type != enums.token_types.FROM or found_line[2].token_type != enums.token_types.TO:
                    errors += [Error("invalid syntax", line_nr)]
                    remaining_tail = tail[length_line-1:]
                    return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)
            if len(found_line) < 4 or len(found_line) > 9:
                errors += [Error("invalid syntax, wrong line length", line_nr)]
                remaining_tail = tail[length_line-1:]
                return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)

            if state == enums.parser_states.SINGLE:
                if length_line == 4:
                    
                    #check for GOTO
                    if found_line[3].token_type == enums.token_types.LINE:
                        check_var = self.findAndReturnVar(found_vars, found_line[1].value)
                        if check_var is not False:
                            var = VariableNode(found_line[3].value, check_var, line_nr, enums.token_types.LINE)
                        else:
                            if found_line[1].token_type == enums.token_types.INT:
                                var = VariableNode(found_line[3].value, Node(found_line[1].value, line_nr, enums.token_types.INT), line_nr, enums.token_types.LINE)
                        tree += [var]
                        remaining_tail = tail[length_line-1:]
                        return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)


                    #check for function decleration 
                    elif found_line[3].token_type == enums.token_types.DECLARE:
                        check_var = self.findAndReturnVar(found_vars, found_line[1].value)
                        if check_var == False:
                            var = VariableNode(found_line[3].value, None, line_nr, enums.token_types.DECLARE)
                            tree += [var]
                            found_funcs[found_line[1].value] = FunctionNode(found_line[1].value, line_nr, [], [], enums.token_types.FUNCTION)
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)
                        else:
                            errors += [Error("function name already taken", line_nr)]
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)
                    
                    #check for function start
                    elif found_line[1].token_type == enums.token_types.START:
                        if found_line[3].value in found_funcs:
                            function = found_funcs[found_line[3].value]
                            tree += [function]
                            state = enums.parser_states.FUNCTION
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr, found_vars, found_funcs, tree, state, errors=errors)
                        else:
                            errors += [Error("function not declared", line_nr)]
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)

                    #check for variable assignement
                    elif found_line[3].token_type == enums.token_types.VAR or found_line[3].token_type == enums.token_types.OUT:
                        var, errors = self.getVarNode(found_line, found_vars, line_nr)
                        if not errors:
                            if found_line[3].token_type == enums.token_types.OUT:
                                var.token_type = enums.token_types.OUT
                            if var.token_type != enums.token_types.OUT:
                                found_vars += [var]
                            tree += [var]
                        remaining_tail = tail[length_line-1:]
                        return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)


                elif length_line == 6:
                    
                    #check for function call
                    if found_line[1].value in found_funcs:
                        func_search = found_funcs[found_line[1].value]
                        if func_search is not False:
                            func = FunctionCall(found_line[1].value, line_nr, None, None, enums.token_types.VAR)
                            if found_line[3].token_type == enums.token_types.INT or found_line[3].token_type == enums.token_types.STRING :
                                input_node = Node(found_line[3].value, line_nr, found_line[3].token_type)
                                func.input = input_node
                            elif found_line[3].token_type == enums.token_types.VAR:
                                temp = self.findAndReturnVar(found_vars, found_line[3].value)
                                if temp is not False:
                                    func.input = input_node
                                else:
                                    errors += [Error("var not declared", line_nr)]
                                    remaining_tail = tail[length_line-1:]
                                    return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)
                            
                            output_node = VariableNode(found_line[5].value, Node(None, line_nr, None), line_nr, enums.token_types.VAR)
                            func.output = output_node

                            tree += [func]
                            found_vars += [output_node]
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)
                        else:
                            errors += [Error("function does not exist", line_nr)]
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)

                    # check for math
                    elif found_line[1].token_type == enums.token_types.VAR and found_line[3].token_type == enums.token_types.VAR:
                        if (found_line[4].token_type is enums.token_types.ADD or
                            found_line[4].token_type is enums.token_types.MUL or
                            found_line[4].token_type is enums.token_types.SUB or
                            found_line[4].token_type is enums.token_types.DIV):

                                var, errors = self.getMathNode(found_line, found_vars, line_nr)
                                if not errors:
                                    tree += [var]
                                remaining_tail = tail[length_line-1:]
                                return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)

                elif length_line == 7 or length_line == 9:
                    
                    #check for if
                    if found_line[1].token_type == enums.token_types.VAR and found_line[5].token_type == enums.token_types.IF:
                        if (found_line[3].token_type == enums.token_types.EQUAL or
                            found_line[3].token_type == enums.token_types.NOTEQUAL or
                            found_line[3].token_type == enums.token_types.GREATER or
                            found_line[3].token_type == enums.token_types.SMALLER or
                            found_line[3].token_type == enums.token_types.EQUALGREATER or
                            found_line[3].token_type == enums.token_types.EQUALSMALLER):
                                    var, errors = self.getIfNode(found_line, found_vars, line_nr)
                                    if not errors:
                                        tree += [var]
                                    remaining_tail = tail[length_line-1:]
                                    return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors)
            #start of function found: 
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
                            else:
                                temp_var = VariableNode(found_line[3].value, temp, function_line_nr, enums.token_types.VAR, enums.node_types.INPUT)
                            new_node.commands += [temp_var]
                            new_node.variables += [temp_var]
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr, found_vars, found_funcs,tree, state, function_line_nr+1, errors=errors)


                        # check for output assignment
                        elif found_line[3].token_type == enums.token_types.OUTPUT:
                            if found_line[1].token_type == enums.token_types.VAR:
                                temp = self.findAndReturnVar(new_node.variables, found_line[1].value)
                                if temp != False:
                                    temp_var = VariableNode(found_line[3].value, temp, function_line_nr, found_line[3].token_type)
                                else:
                                    errors += [Error("var not declared, in function", line_nr)]
                                    remaining_tail = tail[length_line-1:]
                                    return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors) 
                            else:
                                temp_var = VariableNode(found_line[3].value, Node(found_line[1].value, function_line_nr, found_line[1].token_type), function_line_nr, found_line[3].token_type)
                            new_node.commands += [temp_var]
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr, found_vars, found_funcs,tree, state, function_line_nr+1, errors=errors)
                        
                        #check for function end
                        elif found_line[1].token_type == enums.token_types.END:
                            state = enums.parser_states.SINGLE
                            remaining_tail = tail[length_line-1:]
                            tree.pop(-1)
                            found_funcs[found_line[3].value] = new_node
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr, found_vars, found_funcs,tree, state, function_line_nr+1, errors=errors)

                        #check for GOTO
                        elif found_line[3].token_type == enums.token_types.LINE:
                            check_var = self.findAndReturnVar(new_node.variables, found_line[1].value)
                            if check_var is not False:
                                var = VariableNode(found_line[3].value, check_var, function_line_nr, enums.token_types.LINE)
                            else:
                                if found_line[1].token_type == enums.token_types.INT:
                                    var = VariableNode(found_line[3].value, Node(found_line[1].value, function_line_nr, enums.token_types.INT), function_line_nr, enums.token_types.LINE)
                            new_node.commands += [var]
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr, found_vars, found_funcs, tree, state, function_line_nr+1, errors=errors)

                        # check for variable assignement
                        elif found_line[3].token_type == enums.token_types.VAR or found_line[3].token_type == enums.token_types.OUT:
                            var, errors = self.getVarNode(found_line, new_node.variables, function_line_nr)

                            if found_line[3].token_type == enums.token_types.OUT:
                                var.token_type = enums.token_types.OUT
                            if var.token_type != enums.token_types.OUT:
                                new_node.variables += [var]
                            new_node.commands += [var]
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr, found_vars, found_funcs,tree, state, function_line_nr+1, errors=errors)

                    elif length_line == 6:

                        #check for function call
                        if found_line[1].value in found_funcs:
                            func_search = found_funcs[found_line[1].value]
                            if func_search is not False:
                                func = FunctionCall(found_line[1].value, line_nr, None, None, enums.token_types.VAR)
                                if found_line[3].token_type == enums.token_types.INT or found_line[3].token_type == enums.token_types.STRING :
                                    input_node = Node(found_line[3].value, line_nr, found_line[3].token_type)
                                    func.input = input_node
                                elif found_line[3].token_type == enums.token_types.VAR:
                                    temp = self.findAndReturnVar(new_node.variables, found_line[3].value)
                                    if temp is not False:
                                        func.input = temp
                                    else:
                                        errors += [Error("var not declared", line_nr)]
                                        remaining_tail = tail[length_line-1:]
                                        return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)
                                output_node = VariableNode(found_line[5].value, Node(None, line_nr, None), line_nr, enums.token_types.VAR)
                                func.output = output_node
                                
                                new_node.commands += [func]
                                new_node.variables += [output_node]
                                remaining_tail = tail[length_line-1:]
                                return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)
                            else:
                                errors += [(Error("function does not exist", line_nr))]
                                remaining_tail = tail[length_line-1:]
                                return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)

                        # check for math
                        if found_line[1].token_type == enums.token_types.VAR and found_line[3].token_type == enums.token_types.VAR:
                            if (found_line[4].token_type is enums.token_types.ADD or
                                found_line[4].token_type is enums.token_types.MUL or
                                found_line[4].token_type is enums.token_types.SUB or
                                found_line[4].token_type is enums.token_types.DIV):

                                    var, errors = self.getMathNode(found_line, new_node.variables, line_nr)
                                    if not errors:
                                        node.commands +=[var]
                                    remaining_tail = tail[length_line-1:]
                                    return self.parse(remaining_tail, line_nr, found_vars, found_funcs,tree, state, function_line_nr+1, errors=errors)
                    
                    elif length_line == 7 or length_line == 9:

                        #check for if
                        if found_line[1].token_type == enums.token_types.VAR and found_line[5].token_type == enums.token_types.IF:
                            if (found_line[3].token_type == enums.token_types.EQUAL or
                                found_line[3].token_type == enums.token_types.NOTEQUAL or
                                found_line[3].token_type == enums.token_types.GREATER or
                                found_line[3].token_type == enums.token_types.SMALLER or
                                found_line[3].token_type == enums.token_types.EQUALGREATER or
                                found_line[3].token_type == enums.token_types.EQUALSMALLER):
                                        var, errors = self.getIfNode(found_line, new_node.variables, line_nr)
                                        if not errors:
                                            node.commands += [var]
                                        remaining_tail = tail[length_line-1:]
                                        return self.parse(remaining_tail, line_nr, found_vars, found_funcs,tree, state, function_line_nr+1, errors=errors)
            

            errors += [Error("SO WRONG I DONT KNOW WHAT YOUR EVEN TRYING", line_nr)]
            remaining_tail = tail[length_line-1:]
            return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)
    
    def getVarNode(self, found_line : List[lexer.Token], found_vars : List[VariableNode], line_nr : int) -> Tuple[ VariableNode, Error]:
        """getVarNode function, creates variable node

        Args:
            found_line (List[lexer.Token]): line to turn into variable node
            found_vars (List[VariableNode]): already defined variables
            line_nr (int): current line number

        Returns:
            Tuple[Error, VariableNode]: tuple returning made Node or error
        """               
        # check if y var already exists
        errors = []
        check_exist_y = self.findAndReturnVar(found_vars, found_line[3].value)
        if check_exist_y == False:
            #variable does not exist yet
            #check if var x already exists
            if found_line[1].token_type == enums.token_types.VAR:
                check_exist_x = self.findAndReturnVar(found_vars, found_line[1].value)
                if check_exist_x is not False:
                    var = VariableNode(found_line[3].value, check_exist_x, line_nr, enums.token_types.VAR)
                else:
                    errors += [Error("Var x does not exist", line_nr)]
                    return None, errors
            elif found_line[1].token_type == enums.token_types.INT:
                var = VariableNode(found_line[3].value, Node(found_line[1].value, line_nr, enums.token_types.INT), line_nr, enums.token_types.VAR)
            elif found_line[1].token_type == enums.token_types.STRING:
                var = VariableNode(found_line[3].value, Node(found_line[1].value, line_nr, enums.token_types.STRING), line_nr, enums.token_types.VAR)
        else:
            #variable does exist
            #check if var x already exists
            if found_line[1].token_type == enums.token_types.VAR:
                check_exist_x = self.findAndReturnVar(found_vars, found_line[1].value)
                if check_exist_x is not False:
                    check_exist_y.value = check_exist_x
                    check_exist_y.line_nr = line_nr
                    var = check_exist_y
                else:
                    errors += [Error("Var x does not exist", line_nr)]
                    return None, errors
            elif found_line[1].token_type == enums.token_types.INT:
                check_exist_y.value = Node(found_line[1].value, line_nr, enums.token_types.INT)
                check_exist_y.line_nr = line_nr
                var = check_exist_y
            elif found_line[1].token_type == enums.token_types.STRING:
                check_exist_y.value = Node(found_line[1].value, line_nr, enums.token_types.STRING)
                check_exist_y.line_nr = line_nr
                var = check_exist_y
        return var, errors

    def getMathNode(self, found_line : List[lexer.Token], found_vars : List[VariableNode], line_nr : int) -> Tuple[MathNode, Error]:
        """getMathNode function, creates math node 

        Args:
            found_line (List[lexer.Token]): line to turn into math node
            found_vars (List[VariableNode]): already defined variables
            line_nr (int): current line number

        Returns:
            Tuple[MathNode, Error]:tuple returning made Node or error
        """        
        errors = []
        if found_line[1].value == found_line[3].value:
            if (found_line[5].token_type is enums.token_types.INT):
                var = self.findAndReturnVar(found_vars, found_line[1].value)
                nmbr = Node(found_line[5].value, line_nr, found_line[5].token_type, enums.node_types.BASE)
                if var == False:
                    errors += [Error("unknown var", line_nr)]
                    return None, errors
                else:
                    math = MathNode(var, nmbr, line_nr, found_line[4].token_type)
                    return math, errors
            if (found_line[5].token_type is enums.token_types.VAR):
                var1 = self.findAndReturnVar(found_vars, found_line[1].value)
                var2 = self.findAndReturnVar(found_vars, found_line[5].value)
                if var1 == False or var2 == False:
                    errors += [Error("unknown var", line_nr)]
                    return None, errors
                if var1 is not False and var2 is not False:
                    math = MathNode(var1, var2, line_nr, found_line[4].token_type)
                    return math, errors

    def getIfNode(self, found_line : List[lexer.Token], found_vars : List[VariableNode], line_nr : int) -> Tuple[IfNode, Error]:
        """getIfNode function, creates if node 

        Args:
            found_line (List[lexer.Token]): line to turn into if node
            found_vars (List[VariableNode]): already defined variables
            line_nr (int): current line number

        Returns:
            Tuple[IfNode, Error]: tuple returning made Node or error
        """        
        errors = []
        check_exist_value = self.findAndReturnVar(found_vars, found_line[1].value)
        if check_exist_value == False:
            errors += [Error("Variable to if on does not exist", line_nr)]
            return None, errors
        else:
            if found_line[4].token_type == enums.token_types.VAR:
                check_exist_condition = self.findAndReturnVar(found_vars, found_line[4].value)
                if check_exist_condition is False:
                    errors += [Error("condition does not exist", line_nr)]
                    return None, errors
                else:
                    condition = ConditionNode(check_exist_value, check_exist_condition, line_nr, found_line[3].token_type)
            elif found_line[4].token_type == enums.token_types.INT:
                condition = ConditionNode(check_exist_value, Node(found_line[4].value, line_nr, enums.token_types.INT), line_nr, found_line[3].token_type)
            elif found_line[4].token_type == enums.token_types.STRING:
                condition = ConditionNode(check_exist_value, Node(found_line[4].value, line_nr, enums.token_types.STRING), line_nr, found_line[3].token_type)

            if found_line[6].token_type == enums.token_types.VAR:
                check_exist_new_value = self.findAndReturnVar(found_vars, found_line[6].value)
                if check_exist_new_value is False:
                    errors += [Error("new value does not exist", line_nr)]
                    return None, errors
                else:
                    new_value = check_exist_new_value
            elif found_line[6].token_type == enums.token_types.INT:
                new_value = Node(found_line[6].value, line_nr, enums.token_types.INT)
            elif found_line[6].token_type == enums.token_types.STRING:
                new_value = Node(found_line[6].value, line_nr, enums.token_types.STRING)

            if len(found_line) == 9:
                if found_line[7].token_type == enums.token_types.ELSE:
                    if found_line[8].token_type == enums.token_types.VAR:
                        check_exist_new_value_false = self.findAndReturnVar(found_vars, found_line[8].value)
                        if check_exist_new_value_false is False:
                            errors += [Error("new value does not exist", line_nr)]
                            return None, errors
                        else:
                            new_value_false = check_exist_new_value_false
                    elif found_line[8].token_type == enums.token_types.INT:
                        new_value_false = Node(found_line[8].value, line_nr, enums.token_types.INT)
                    elif found_line[8].token_type == enums.token_types.STRING:
                        new_value_false = Node(found_line[8].value, line_nr, enums.token_types.STRING)
            
            var = IfNode(check_exist_value, condition, new_value, new_value_false, line_nr, enums.token_types.IF)
        return var, errors

    def getLine(self, tokens : List[lexer.Token], line : List[lexer.Token]=[]) -> List[lexer.Token]:
        """getLine function, find a line from list of tokens

        Args:
            tokens (List[lexer.Token]): all found tokens
            line (List[lexer.Token], optional): line of tokens that is found. Defaults to [].

        Returns:
            List[lexer.Token]: found line
        """        
        
        if len(tokens) == 0:
            return []
        head, *tail = tokens 
        if head.token_type != enums.token_types.FROM:
            return [head] + self.getLine(tail)
        return []

    def findAndReturnVar(self,  search_area : List[VariableNode], value_to_find : str ) -> Union[VariableNode, bool]:
        """findAndReturnVar function, find a variable in list by name

        Args:
            search_area (List[VariableNode]): list of variable nodes
            value_to_find (str): variable name to find

        Returns:
            Union[VariableNode, bool]: copy of found variable or False
        """        
        if not search_area:
            return False
        head, *tail = search_area
        if head.variable_name == value_to_find:
            return copy.copy(head)
        return self.findAndReturnVar( tail, value_to_find)


class Visitor(object):
    def __init__(self):
        pass
    def divide(self, lhs : int, rhs: int):
        return lhs / rhs

    node_types = TypeVar(Node, VariableNode, MathNode, ConditionNode, IfNode)
    def visitAl(self, node_list : List[Node], node_list_copy : List[Node], variables : dict={}, found_funcs : dict = {}) -> Union[Error,dict]:

        if len(node_list) == 0:
            return variables
        head, *tail = node_list
        variables_copy = copy.copy(variables)

        if head.token_type == enums.token_types.LINE:
            start_line, variables_copy = head.visit(variables_copy, found_funcs)
            if type(start_line) is Error:
                return start_line
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
        

    def visitNode(self, node : Node, variables: dict , found_funcs : dict = {} ) -> Tuple[Union[Error,lit_types], dict]:
        copy_node = copy.copy(node)
        return copy_node.value, variables

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
            else:
                line_number, variables_copy = copy_node.value.visit(variables_copy, found_funcs)
            return line_number, variables_copy # returned echte ints, geen nodes

        elif copy_node.token_type == enums.token_types.DECLARE:
            return copy_node, variables_copy


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
            function = lambda x, y: self.divide(x,y) # DECORATED
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
        # items = list(map(lambda x: int(x) if x.isnumeric() else x, items)) #HOGERE ORDE FUNCTIE
        elif type(items[0]) == int and type(items[1]) == int:
            result = functools.reduce(function, items) #HOGERE ORDE FUNCTIE
            return result, variables_copy
        else:
            error = Error("cant compare variables of different type", copy_node.line_nr)
            return error, variables_copy

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

    def visitFunctionCall(self, node : FunctionNode, variables: dict , found_funcs : dict = {}) -> Tuple[Union[Error, VariableNode], dict]:
        variables_copy = copy.copy(variables)
        copy_node = copy.copy(node)

        function = found_funcs[copy_node.value]
        function_output, variables_copy = function.visit(copy_node.input, variables_copy, found_funcs)
        copy_node.output.value = function_output
        variables_copy[copy_node.output.variable_name] = copy_node.output.value
        return function_output, variables_copy

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
