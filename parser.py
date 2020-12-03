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
        return '{value}'.format(
            value=self.value
        )

    def __repr__(self) -> str:
        return self.__str__()

    def visit(self, variables : dict, function_body : bool) -> lit_types:
        visitor = Visitor()
        return visitor.visitNode(self, variables, function_body)

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

    def visit(self,variables : dict, function_body : bool) -> Node:
        visitor = Visitor()
        return visitor.visitVariable(self, variables, function_body)

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

    def visit(self, variables : dict, function_body : bool) -> Node:
        visitor = Visitor()
        return visitor.visitMath(self, variables, function_body)

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

    def visit(self, variables: dict, function_body : bool) -> Node:
        visitor = Visitor()
        return visitor.visitCondition(self, variables, function_body)

class IfNode(Node):
    """IfNode class, inherits from Node
    """    
    def __init__(self, value : Node, condition : ConditionNode, new_value : Node, line_nr : int, token_type = enums.token_types, node_type: enums.node_types=enums.node_types.IF):
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

    def visit(self, variables : dict, function_body : bool) -> Node:
        visitor = Visitor()
        return visitor.visitIF(self, variables, function_body)


#TODO visitor
dif_nodes = TypeVar(Node, MathNode, IfNode, VariableNode)
class FunctionNode(Node):
    """FunctionNode class, inherits from Node"""    
    # value = function name
    def __init__(self, value : Node, line_nr : int, commands: List[dif_nodes]=[], input : List[Node]=[], output : List[Node]=[], variables: List[VariableNode]=[], token_type : enums.token_types=enums.token_types.FUNCTION, node_type : enums.node_types.FUNCTION=enums.node_types.FUNCTION):
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
        self.input = input
        self.output = output
        self.variables = variables
    
    def __str__(self) -> str:
        return '{value}\n body: ({commands}), \n input:{input}, \n output:{output} \n'.format(
            value = self.value,
            commands = self.commands,
            input = self.input,
            output = self.output
        )

    def __repr__(self) -> str:
        return self.__str__()

    def visit(self, variables : dict, function_body : bool):
        visitor = Visitor()
        return visitor.visitFunction(self, variables, function_body)

class Parser(object):
    def __init__(self):
        pass

    list_types = TypeVar(Node, VariableNode, MathNode, Error)
    def parse(  self, token_list : List[lexer.Token], line_nr : int = 1, found_vars : List[VariableNode]=[], found_func_names : List[str]=[], 
                found_funcs : dict = {}, tree : List[list_types] = [], state :enums.parser_states=enums.parser_states.SINGLE, function_line_nr : int = 1, errors : List[Error]=[]) -> List[list_types]:
        """parser function

        Args:
            token_list (List[lexer.Token]): list of tokens
            line_nr (int, optional): linenumber of current found line. Defaults to 1.
            found_vars (List[VariableNode], optional): found variables in code. Defaults to [].
            found_func_names (List[str], optional): found function names in code. Defaults to [].
            found_funcs (List[FunctionNode], optional): found function list in code. Defaults to [].
            tree (List[list_types], optional): AST. Defaults to [].
            state (enums.parser_states, optional):current state. Defaults to enums.parser_states.SINGLE.
            function_line_nr (int, optional): line number within possible function. Defaults to 1.
            errors (List[Error], optional): list of found errors. Defaults to [].

        Returns:
            List[list_types]: [description]
        """        
        found_vars = copy.copy(found_vars)
        found_func_names = copy.copy(found_func_names)
        found_funcs = copy.copy(found_funcs)
        errors = copy.copy(errors)
        tree = copy.copy(tree)

        if len( errors ) > 0:
            return errors

        if len( token_list ) == 0:
            return tree

        head, *tail = token_list

        value = head.value
        token_type = head.token_type
        if token_type == enums.token_types.FROM:
            found_line = [head] + self.getLine(tail)

            # based on length of line start assigning
            length_line = len(found_line)
            if len(found_line) != 6:
                if found_line[0].token_type != enums.token_types.FROM or found_line[2].token_type != enums.token_types.TO:
                    errors.append(Error("invalid syntax", line_nr))
                    remaining_tail = tail[length_line-1:]
                    return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, found_funcs, tree, state, errors=errors)
            if len(found_line) < 4 or len(found_line) > 7:
                errors.append(Error("invalid syntax, wrong line length", line_nr))
                remaining_tail = tail[length_line-1:]
                return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, found_funcs, tree, state, errors=errors)

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
                        tree.append(var)
                        remaining_tail = tail[length_line-1:]
                        return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, found_funcs, tree, state, errors=errors)


                    #check for function decleration 
                    elif found_line[3].token_type == enums.token_types.DECLARE:
                        check_var = self.findAndReturnVar(found_vars, found_line[1].value)
                        if check_var == False:
                            var = VariableNode(found_line[3].value, None, line_nr, enums.token_types.DECLARE)
                            tree.append(var)
                            found_funcs[found_line[1].value] = FunctionNode(found_line[1].value, line_nr, [], [], [], [], enums.token_types.FUNCTION)
                            found_func_names.append(found_line[1].value) #TODO remove niet meer nodig door dict
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, found_funcs, tree, state, errors=errors)
                        else:
                            errors.append(Error("function name already taken", line_nr))
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, found_funcs, tree, state, errors=errors)
                    
                    #check for function start
                    elif found_line[1].token_type == enums.token_types.START:
                        if found_line[3].value in found_funcs:
                            function = found_funcs[found_line[3].value]
                            tree.append(function) 
                            state = enums.parser_states.FUNCTION
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr, found_vars, found_func_names, found_funcs, tree, state, errors=errors)
                        else:
                            errors.append(Error("function not declared", line_nr))
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, found_funcs, tree, state, errors=errors)

                    #check for variable assignement
                    elif found_line[3].token_type == enums.token_types.VAR or found_line[3].token_type == enums.token_types.OUT:
                        var, errors = self.getVarNode(found_line, found_vars, line_nr)
                        if not errors:
                            if found_line[3].token_type == enums.token_types.OUT:
                                var.token_type = enums.token_types.OUT
                            if var.token_type != enums.token_types.OUT:
                                found_vars.append(var)
                            tree.append(var)
                        remaining_tail = tail[length_line-1:]
                        return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, found_funcs, tree, state, errors=errors)


                elif length_line == 6:
                    
                    #check for function call
                    if found_line[1].value in found_func_names:
                        func_search = found_funcs[found_line[1].value]
                        if func_search is not False:
                            func = copy.copy(func_search)
                            if found_line[3].token_type == enums.token_types.INT or found_line[3].token_type == enums.token_types.STRING :
                                input_node = Node(found_line[3].value, line_nr, found_line[3].token_type)
                                func.input.append(input_node)
                            elif found_line[3].token_type == enums.token_types.VAR:
                                temp = self.findAndReturnVar(found_vars, found_line[3].value)
                                if temp is not False:
                                    func.input.append(temp)
                                else:
                                    errors.append(Error("var not declared", line_nr))
                                    remaining_tail = tail[length_line-1:]
                                    return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, found_funcs, tree, state, errors=errors)

                            func.output.append(VariableNode(found_line[5].value, Node(None, line_nr, None), line_nr, enums.token_types.VAR))
                            
                            var = VariableNode(found_line[5].value, func, line_nr, enums.token_types.FUNCTION)
                            tree.append(var)
                            found_vars.append(var)
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, found_funcs, tree, state, errors=errors)
                        else:
                            errors.append(Error("function does not exist", line_nr))
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, found_funcs, tree, state, errors=errors)

                    # check for math
                    elif found_line[1].token_type == enums.token_types.VAR and found_line[3].token_type == enums.token_types.VAR:
                        if (found_line[4].token_type is enums.token_types.ADD or
                            found_line[4].token_type is enums.token_types.MUL or
                            found_line[4].token_type is enums.token_types.SUB or
                            found_line[4].token_type is enums.token_types.DIV):

                                var, errors = self.getMathNode(found_line, found_vars, line_nr)
                                if not errors:
                                    tree.append(var)
                                remaining_tail = tail[length_line-1:]
                                return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, found_funcs, tree, state, errors=errors)

                elif length_line == 7:
                    
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
                                        tree.append(var)
                                    remaining_tail = tail[length_line-1:]
                                    return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, found_funcs, tree, state, errors)
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
                            new_node.commands.append(temp_var)
                            new_node.variables.append(temp_var)
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr, found_vars, found_func_names, found_funcs,tree, state, function_line_nr+1, errors=errors)


                        # check for output assignment
                        elif found_line[3].token_type == enums.token_types.OUTPUT:
                            if found_line[1].token_type == enums.token_types.VAR:
                                temp = self.findAndReturnVar(new_node.variables, found_line[1].value)
                                if temp != False:
                                    temp_var = VariableNode(found_line[3].value, temp, function_line_nr, found_line[3].token_type)
                                else:
                                    errors.append(Error("var not declared, in function", line_nr))
                                    remaining_tail = tail[length_line-1:]
                                    return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, found_funcs, tree, state, errors=errors) 
                            else:
                                temp_var = VariableNode(found_line[3].value, Node(found_line[1].value, function_line_nr, found_line[1].token_type), function_line_nr, found_line[3].token_type)
                            new_node.commands.append(temp_var)
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr, found_vars, found_func_names, found_funcs,tree, state, function_line_nr+1, errors=errors)
                        
                        #check for function end
                        elif found_line[1].token_type == enums.token_types.END:
                            state = enums.parser_states.SINGLE
                            remaining_tail = tail[length_line-1:]
                            tree.pop(-1)
                            found_funcs[found_line[3].value] = new_node
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr, found_vars, found_func_names, found_funcs,tree, state, function_line_nr+1, errors=errors)

                        #check for GOTO
                        elif found_line[3].token_type == enums.token_types.LINE:
                            check_var = self.findAndReturnVar(new_node.variables, found_line[1].value)
                            if check_var is not False:
                                var = VariableNode(found_line[3].value, check_var, function_line_nr, enums.token_types.LINE)
                            else:
                                if found_line[1].token_type == enums.token_types.INT:
                                    var = VariableNode(found_line[3].value, Node(found_line[1].value, function_line_nr, enums.token_types.INT), function_line_nr, enums.token_types.LINE)
                            new_node.commands.append(var)
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr, found_vars, found_func_names, found_funcs, tree, state, function_line_nr+1, errors=errors)

                        # check for variable assignement
                        elif found_line[3].token_type == enums.token_types.VAR or found_line[3].token_type == enums.token_types.OUT:
                            var, errors = self.getVarNode(found_line, new_node.variables, function_line_nr)

                            if found_line[3].token_type == enums.token_types.OUT:
                                var.token_type = enums.token_types.OUT
                            if var.token_type != enums.token_types.OUT:
                                new_node.variables.append(var)
                            new_node.commands.append(var)
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr, found_vars, found_func_names, found_funcs,tree, state, function_line_nr+1, errors=errors)

                    elif length_line == 6:

                        #check for function call
                        if found_line[1].value in found_func_names:
                            func_search = found_funcs[found_line[1].value]
                            if func_search is not False:
                                func = copy.copy(func_search)
                                if found_line[3].token_type == enums.token_types.INT or found_line[3].token_type == enums.token_types.STRING :
                                    func.input.append(Node(found_line[3].value, line_nr, found_line[3].token_type))
                                elif found_line[3].token_type == enums.token_types.VAR:
                                    temp = self.findAndReturnVar(new_node.variables, found_line[3].value)
                                    if temp is not False:
                                        func.input.append(temp)
                                    else:
                                        errors.append(Error("var not declared, in function", line_nr))
                                        remaining_tail = tail[length_line-1:]
                                        return self.parse(remaining_tail, line_nr+1, new_node.variables, found_func_names, found_funcs, tree, state, errors=errors)

                                func.output.append(VariableNode(found_line[5].value, Node(None, line_nr, None), line_nr, enums.token_types.VAR))
                                
                                var = VariableNode(found_line[5].value, func, line_nr, enums.token_types.VAR)
                                new_node.commands.append(var)
                                new_node.variables.append(var)
                                remaining_tail = tail[length_line-1:]
                                return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, found_funcs, tree, state, errors=errors)
                            else:
                                errors.append(Error("function does not exist", line_nr))
                                remaining_tail = tail[length_line-1:]
                                return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, found_funcs, tree, state, errors=errors)

                        # check for math
                        if found_line[1].token_type == enums.token_types.VAR and found_line[3].token_type == enums.token_types.VAR:
                            if (found_line[4].token_type is enums.token_types.ADD or
                                found_line[4].token_type is enums.token_types.MUL or
                                found_line[4].token_type is enums.token_types.SUB or
                                found_line[4].token_type is enums.token_types.DIV):

                                    var, errors = self.getMathNode(found_line, new_node.variables, line_nr)
                                    if not errors:
                                        node.commands.append(var)
                                    remaining_tail = tail[length_line-1:]
                                    return self.parse(remaining_tail, line_nr, found_vars, found_func_names, found_funcs,tree, state, function_line_nr+1, errors=errors)
                    
                    elif length_line == 7:

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
                                            node.commands.append(var)
                                        remaining_tail = tail[length_line-1:]
                                        return self.parse(remaining_tail, line_nr, found_vars, found_func_names, found_funcs,tree, state, function_line_nr+1, errors=errors)
            

            errors.append(Error("SO WRONG I DONT KNOW WHAT YOUR EVEN TRYING", line_nr))
            remaining_tail = tail[length_line-1:]
            return self.parse(remaining_tail, line_nr+1, found_vars, found_func_names, found_funcs, tree, state, errors=errors)
    
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
                    errors.append(Error("Var x does not exist", line_nr))
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
                    errors.append(Error("Var x does not exist", line_nr))
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
                    errors.append(Error("unknown var", line_nr))
                    return None, errors
                else:
                    math = MathNode(var, nmbr, line_nr, found_line[4].token_type)
                    return math, errors
            if (found_line[5].token_type is enums.token_types.VAR):
                var1 = self.findAndReturnVar(found_vars, found_line[1].value)
                var2 = self.findAndReturnVar(found_vars, found_line[5].value)
                if var1 == False or var2 == False:
                    errors.append(Error("unknown var", line_nr))
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
            errors.append(Error("Variable to if on does not exist", line_nr))
            return None, errors
        else:
            if found_line[4].token_type == enums.token_types.VAR:
                check_exist_condition = self.findAndReturnVar(found_vars, found_line[4].value)
                if check_exist_condition is False:
                    errors.append(Error("condition does not exist", line_nr))
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
                    errors.append(Error("new value does not exist", line_nr))
                    return None, errors
                else:
                    new_value = check_exist_new_value
            elif found_line[6].token_type == enums.token_types.INT:
                new_value = Node(found_line[6].value, line_nr, enums.token_types.INT)
            elif found_line[6].token_type == enums.token_types.STRING:
                new_value = Node(found_line[6].value, line_nr, enums.token_types.STRING)
            
            var = IfNode(check_exist_value, condition, new_value, line_nr, enums.token_types.IF)
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

    def findAndReturnFunc(self,  search_area : List[FunctionNode], value_to_find : str ) -> Union[FunctionNode,bool]:
        """findAndReturnFunc function, find a function in list by name

        Args:
            search_area (List[VariableNode]): list of function nodes
            value_to_find (str): variable name to find

        Returns:
            Union[VariableNode, bool]: copy of found function or False
        """     
        if not search_area:
            return False
        head, *tail = search_area
        if head.value == value_to_find:
            return copy.copy(head)
        return self.findAndReturnFunc( tail, value_to_find)


class Visitor(object):
    def __init__(self):
        pass
    def divide(self, lhs : int, rhs: int):
        return lhs / rhs

    #test met testroutines
    node_types = TypeVar(Node, VariableNode, MathNode, ConditionNode, IfNode)
    def visitAl(self, node_list : List[Node], copy_list :List[node_types], variables : dict={}, function_body : bool=False) -> Union[Error,dict]:
        
        if len(node_list) == 0:
            return variables
        head, *tail = node_list
        variables_copy = copy.copy(variables)

        #TODO fix function calls

        if head.token_type == enums.token_types.LINE:
            start_line, variables_copy = head.visit(variables_copy, function_body)
            if type(start_line) is Error:
                return start_line
            start_line = str(start_line)
            if not start_line.isnumeric():
                error = Error("Line number to jump to not int", head.line_nr)
                return error
            if int(start_line) <= len(tail):
                start_line = int(start_line) - 1
                tail = copy.copy(tail[int(start_line):])
            else:
                tail= []
            return self.visitAl(tail, copy_list, variables_copy, function_body)
        else:
            pos_error, variables_copy = head.visit(variables_copy, function_body)
            if type(pos_error) is Error:
                return pos_error
        return self.visitAl(tail, copy_list, variables_copy, function_body)
        

    def visitNode(self, node : Node, variables: dict, function_body : bool ) -> Tuple[Union[Error,lit_types], dict]:
        copy_node = copy.copy(node)
        return copy_node.value, variables

    def visitVariable(self, node : VariableNode, variables: dict, function_body : bool ) -> Tuple[Union[Error,VariableNode], dict]:
        copy_node = copy.copy(node)
        variables_copy = copy.copy(variables)

        if copy_node.token_type == enums.token_types.OUT:
            if copy_node.value.token_type == enums.token_types.VAR or copy_node.value.token_type == enums.token_types.OUTPUT:
                printable = variables_copy[copy_node.value.variable_name]
                printable, variables_copy = printable.visit(variables_copy, function_body)
                if type(printable) is Error:
                    return printable, variables_copy
            elif copy_node.value.token_type == enums.token_types.FUNCTION:
                printable, variables_copy = copy_node.value.visit(variables_copy, True)
                if type(printable) is Error:
                    return printable, variables_copy
                printable = variables_copy[copy_node.value.variable_name]
            else:
                printable, variables_copy = copy_node.value.visit(variables_copy, function_body)
                if type(printable) is Error:
                    return printable, variables_copy
            if function_body is False:
                print(printable)
                return printable, variables_copy
            else:
                return printable, variables_copy
        elif copy_node.token_type == enums.token_types.LINE:
            if copy_node.value.token_type == enums.token_types.VAR:
                line_number = variables_copy[copy_node.value.variable_name]
            else:
                line_number, variables_copy = copy_node.value.visit(variables_copy, function_body)
                if type(line_number) is Error:
                    return line_number, variables_copy
            return line_number, variables_copy
        elif copy_node.token_type == enums.token_types.DECLARE:
            return copy_node, variables_copy
        elif copy_node.token_type == enums.token_types.VAR:
            if copy_node.value.token_type == enums.token_types.FUNCTION:
                function_result ,variables_copy = copy_node.value.visit(variables_copy, function_body)
                variables_copy[copy_node.value] = function_result
                return variables_copy[copy_node.value], variables_copy
            elif copy_node.value.value == "INPUT":
                input_value = variables_copy["INPUT"]
                result, variables_copy = input_value.visit(variables_copy, function_body)
            else:
                result, variables_copy = copy_node.value.visit(variables_copy, function_body)
            if type(result) is Error:
                return result, variables_copy
            variables_copy[copy_node.variable_name] = result
            return result, variables_copy
        elif copy_node.token_type == enums.token_types.OUTPUT:
            if copy_node.value.token_type == enums.token_types.VAR:
                variables_copy[copy_node.variable_name] = copy_node.value
                return copy_node, variables_copy
            if copy_node.value.value == "INPUT":
                input_value = variables_copy["INPUT"]
                result, variables_copy = input_value.visit(variables_copy, function_body) 
            else:
                result, variables_copy = copy_node.value.visit(variables_copy, function_body)
            if type(result) is Error:
                return result, variables_copy
            variables_copy[copy_node.variable_name] = result
            return result, variables_copy
        else: # literals
            value, variables_copy = copy_node.value.visit(variables_copy, function_body)
            if type(value) is Error:
                return value, variables_copy
            return value, variables_copy

    def visitMath(self, node : MathNode, variables: dict, function_body : bool) -> Tuple[Union[Error,int], dict]:
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
            item_1, _ = copy_node.value.visit(variables, function_body)
            item_2 ,_ = copy_node.rhs.visit(variables, function_body)
            if type(item_1) is Error or type(item_2) is Error:
                error = Error("error in math variables", copy_node.line_nr)
                return error, variables_copy
            items = [item_1, item_2]
        else:
            item_1, _ = copy_node.value.visit(variables, function_body)
            item_2, _ = copy_node.rhs.visit(variables, function_body)
            if type(item_1) is Error or type(item_2) is Error:
                error = Error("error in math variables", copy_node.line_nr)
                return error, variables_copy
            items = [item_1, item_2]

        items = list(map(lambda x: int(x) if x.isnumeric() else x, items)) #HOGERE ORDE FUNCTIE
        new_value = Node(functools.reduce(function, items), node.line_nr, enums.token_types.INT) #HOGERE ORDE FUNCTIE
        if copy_node.value.variable_name in variables_copy:
            variables_copy[copy_node.value.variable_name] = new_value
            return new_value, variables_copy
        else:
            error = Error("Math statement on unknown variable", copy_node.line_nr)
            return error, variables_copy

    def visitCondition(self, node : ConditionNode, variables: dict, function_body : bool) -> Tuple[Union[Error, bool], dict]:
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

        item_1, variables_copy  = copy_node.value.visit(variables_copy, function_body)
        item_2, variables_copy = copy_node.condition.visit(variables_copy, function_body)
        if copy_node.condition.token_type == enums.token_types.VAR:
            item_2, variables_copy = copy_node.condition.visit(variables_copy, function_body)
        
        items = [item_1, item_2]
        if not items[0].isnumeric() and not items[1].isnumeric():
            if (copy_node.token_type == enums.token_types.EQUAL or
                copy_node.token_type == enums.token_types.NOTEQUAL):
                result = functools.reduce(function, items) #HOGERE ORDE FUNCTIE
                return result, variables_copy
        else:
            items = list(map(lambda x: int(x) if x.isnumeric() else x, items)) #HOGERE ORDE FUNCTIE
            result = functools.reduce(function, items) #HOGERE ORDE FUNCTIE
            return result, variables_copy

    def visitIF(self, node : IfNode, variables: dict, function_body : bool) -> Tuple[Union[Error,lit_types], dict]:
        variables_copy = copy.copy(variables)
        copy_node = copy.copy(node)
        result, variables_copy = copy_node.condition.visit(variables_copy, function_body)
        if result == True:
            new_value = Node(node.new_value, node.line_nr, node.new_value.token_type)
            if copy_node.value.variable_name in variables_copy:
                item = variables_copy[copy_node.value.variable_name]
                variables_copy[copy_node.value.variable_name] = new_value
                return new_value, variables_copy 
            else:
                error = Error("if statement on undeclared variable", copy_node.line_nr)
                return error, variables_copy  
        return copy_node.value, variables_copy

    def visitFunction(self, node : FunctionNode, variables: dict, function_body : bool) -> Tuple[Union[Error, VariableNode], dict]:
        variables_copy = copy.copy(variables)
        copy_node = copy.copy(node)
        function_variables = {}

        print("ind visitFunction")


        input_node = VariableNode("INPUT", Node(copy_node.input[0],copy_node.line_nr, copy_node.input[0].token_type) , copy_node.line_nr, enums.token_types.VAR)
        function_variables["INPUT"] = input_node
        copy_node.commands.insert(0,input_node)
        new_function_variables = self.visitAl(copy_node.commands, copy_node.commands, function_variables, function_body)

        if type(new_function_variables) is Error:
            return new_function_variables, variables_copy

        if 'OUTPUT' in new_function_variables:
            result = new_function_variables["OUTPUT"]
            result, new_function_variables = result.value.visit(new_function_variables, function_body)
            result = Node(result, copy_node.line_nr, enums.token_types.OUTPUT)
            new_node = VariableNode(copy_node.value, result, copy_node.line_nr, result.token_type)
            return new_node, variables_copy
        else:
            error = Error("No output specified in function", copy_node.line_nr)
            return error, variables_copy
