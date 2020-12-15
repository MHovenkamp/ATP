from typing import List, TypeVar, Union, Tuple
import functools
import operator
import copy

import enums
import support
import lexer


class Parser(object):
    def __init__(self):
        pass

    list_types = TypeVar(support.Node, support.VariableNode, support.MathNode, support.Error)
    # parser :: List[lexer.Token], int, List[support.VariableNode], dict, List[list_types], enums.parser_states, int, List[support.Error] -> Tuple(List[list_types], dict)
    def parse(  self, token_list : List[lexer.Token], line_nr : int = 1, found_vars : List[support.VariableNode]=[],
                found_funcs : dict = {}, tree : List[list_types] = [], state :enums.parser_states=enums.parser_states.SINGLE, function_line_nr : int = 1, errors : List[support.Error]=[]) -> Tuple[List[list_types], dict]:
        """main parser function

        Args:
            token_list (List[lexer.Token]): list of tokens to parse
            line_nr (int, optional): current line number. Defaults to 1.
            found_vars (List[support.VariableNode], optional): Al found variables up until current recursion. Defaults to [].
            found_funcs (dict, optional): Al found functions up until current recursion. Defaults to {}.
            tree (List[list_types], optional): AST. Defaults to [].
            state (enums.parser_states, optional): current state. Defaults to enums.parser_states.SINGLE.
            function_line_nr (int, optional): current line number inside function. Defaults to 1.
            errors (List[support.Error], optional): list of errors found in parserd line. Defaults to [].

        Returns:
            Tuple[List[list_types], dict]: return either list of errors or created AST and al found functions
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
                    errors += [support.Error("invalid syntax", line_nr)]
                    remaining_tail = tail[length_line-1:]
                    return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)
            if len(found_line) < 4 or len(found_line) > 9:
                errors += [support.Error("invalid syntax, wrong line length", line_nr)]
                remaining_tail = tail[length_line-1:]
                return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)

            if state == enums.parser_states.SINGLE:
                if length_line == 4:
                    
                    #check for GOTO
                    if found_line[3].token_type == enums.token_types.LINE:
                        check_var = self.findAndReturnVar(found_vars, found_line[1].value)
                        if check_var is not False:
                            var = support.VariableNode(found_line[3].value, check_var, line_nr, enums.token_types.LINE)
                        else:
                            if found_line[1].token_type == enums.token_types.INT:
                                var = support.VariableNode(found_line[3].value, support.Node(found_line[1].value, line_nr, enums.token_types.INT), line_nr, enums.token_types.LINE)
                        tree += [var]
                        remaining_tail = tail[length_line-1:]
                        return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)
                    #check for Error
                    if found_line[3].token_type == enums.token_types.ERR:
                        var = support.VariableNode(found_line[3].value, found_line[1].value, line_nr, enums.token_types.ERR)
                        tree += [var]
                        remaining_tail = tail[length_line-1:]
                        return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)

                    #check for function decleration 
                    elif found_line[3].token_type == enums.token_types.DECLARE:
                        check_var = self.findAndReturnVar(found_vars, found_line[1].value)
                        if check_var == False:
                            var = support.VariableNode(found_line[3].value, None, line_nr, enums.token_types.DECLARE)
                            tree += [var]
                            found_funcs[found_line[1].value] = support.FunctionNode(found_line[1].value, line_nr, [], [], enums.token_types.FUNCTION)
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)
                        else:
                            errors += [support.Error("function name already taken", line_nr)]
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
                            errors += [support.Error("function not declared", line_nr)]
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
                            func = support.FunctionCall(found_line[1].value, line_nr, None, None, enums.token_types.VAR)
                            if found_line[3].token_type == enums.token_types.INT or found_line[3].token_type == enums.token_types.STRING :
                                input_node = support.Node(found_line[3].value, line_nr, found_line[3].token_type)
                                func.input = input_node
                            elif found_line[3].token_type == enums.token_types.VAR:
                                temp = self.findAndReturnVar(found_vars, found_line[3].value)
                                if temp is not False:
                                    func.input = input_node
                                else:
                                    errors += [support.Error("var not declared", line_nr)]
                                    remaining_tail = tail[length_line-1:]
                                    return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)
                            
                            output_node = support.VariableNode(found_line[5].value, support.Node(None, line_nr, None), line_nr, enums.token_types.VAR)
                            func.output = output_node

                            tree += [func]
                            found_vars += [output_node]
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)
                        else:
                            errors += [support.Error("function does not exist", line_nr)]
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
                                temp_var = support.VariableNode(found_line[3].value, support.Node(found_line[1].value, function_line_nr, enums.token_types.INPUT), function_line_nr, enums.token_types.VAR, enums.node_types.INPUT)
                            else:
                                temp_var = support.VariableNode(found_line[3].value, temp, function_line_nr, enums.token_types.VAR, enums.node_types.INPUT)
                            new_node.commands += [temp_var]
                            new_node.variables += [temp_var]
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr, found_vars, found_funcs,tree, state, function_line_nr+1, errors=errors)


                        # check for output assignment
                        elif found_line[3].token_type == enums.token_types.OUTPUT:
                            if found_line[1].token_type == enums.token_types.VAR:
                                temp = self.findAndReturnVar(new_node.variables, found_line[1].value)
                                if temp != False:
                                    temp_var = support.VariableNode(found_line[3].value, temp, function_line_nr, found_line[3].token_type)
                                else:
                                    errors += [support.Error("var not declared, in function", line_nr)]
                                    remaining_tail = tail[length_line-1:]
                                    return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors) 
                            else:
                                temp_var = support.VariableNode(found_line[3].value, support.Node(found_line[1].value, function_line_nr, found_line[1].token_type), function_line_nr, found_line[3].token_type)
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
                                var = support.VariableNode(found_line[3].value, check_var, function_line_nr, enums.token_types.LINE)
                            else:
                                if found_line[1].token_type == enums.token_types.INT:
                                    var = support.VariableNode(found_line[3].value, support.Node(found_line[1].value, function_line_nr, enums.token_types.INT), function_line_nr, enums.token_types.LINE)
                            new_node.commands += [var]
                            remaining_tail = tail[length_line-1:]
                            return self.parse(remaining_tail, line_nr, found_vars, found_funcs, tree, state, function_line_nr+1, errors=errors)

                        #check for Error
                        elif found_line[3].token_type == enums.token_types.ERR:
                            var = support.VariableNode(found_line[3].value, found_line[1].value, line_nr, enums.token_types.ERR)
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
                                func = support.FunctionCall(found_line[1].value, line_nr, None, None, enums.token_types.VAR)
                                if found_line[3].token_type == enums.token_types.INT or found_line[3].token_type == enums.token_types.STRING :
                                    input_node = support.Node(found_line[3].value, line_nr, found_line[3].token_type)
                                    func.input = input_node
                                elif found_line[3].token_type == enums.token_types.VAR:
                                    temp = self.findAndReturnVar(new_node.variables, found_line[3].value)
                                    if temp is not False:
                                        func.input = temp
                                    else:
                                        errors += [support.Error("var not declared", line_nr)]
                                        remaining_tail = tail[length_line-1:]
                                        return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)
                                output_node = support.VariableNode(found_line[5].value, support.Node(None, line_nr, None), line_nr, enums.token_types.VAR)
                                func.output = output_node
                                
                                new_node.commands += [func]
                                new_node.variables += [output_node]
                                remaining_tail = tail[length_line-1:]
                                return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)
                            else:
                                errors += [(support.Error("function does not exist", line_nr))]
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
            
            errors += [support.Error("SO WRONG I DONT KNOW WHAT YOUR EVEN TRYING", line_nr)]
            remaining_tail = tail[length_line-1:]
            return self.parse(remaining_tail, line_nr+1, found_vars, found_funcs, tree, state, errors=errors)
    
    # getVarNode :: List[lexer.Token], List[support.VariableNode], int -> Tuple(support.VariableNode, support.Error)
    def getVarNode(self, found_line : List[lexer.Token], found_vars : List[support.VariableNode], line_nr : int) -> Tuple[ support.VariableNode, support.Error]:
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
                    var = support.VariableNode(found_line[3].value, check_exist_x, line_nr, enums.token_types.VAR)
                else:
                    errors += [support.Error("Var x does not exist", line_nr)]
                    return None, errors
            elif found_line[1].token_type == enums.token_types.INT:
                var = support.VariableNode(found_line[3].value, support.Node(found_line[1].value, line_nr, enums.token_types.INT), line_nr, enums.token_types.VAR)
            elif found_line[1].token_type == enums.token_types.STRING:
                var = support.VariableNode(found_line[3].value, support.Node(found_line[1].value, line_nr, enums.token_types.STRING), line_nr, enums.token_types.VAR)
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
                    errors += [support.Error("Var x does not exist", line_nr)]
                    return None, errors
            elif found_line[1].token_type == enums.token_types.INT:
                check_exist_y.value = support.Node(found_line[1].value, line_nr, enums.token_types.INT)
                check_exist_y.line_nr = line_nr
                var = check_exist_y
            elif found_line[1].token_type == enums.token_types.STRING:
                check_exist_y.value = support.Node(found_line[1].value, line_nr, enums.token_types.STRING)
                check_exist_y.line_nr = line_nr
                var = check_exist_y
        return var, errors

    # getMathNode :: List[lexer.Token], List[support.VariableNode], int -> Tuple(support.MathNode, support.Error)
    def getMathNode(self, found_line : List[lexer.Token], found_vars : List[support.VariableNode], line_nr : int) -> Tuple[support.MathNode, support.Error]:
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
                nmbr = support.Node(found_line[5].value, line_nr, found_line[5].token_type, enums.node_types.BASE)
                if var == False:
                    errors += [support.Error("unknown var", line_nr)]
                    return None, errors
                else:
                    math = support.MathNode(var, nmbr, line_nr, found_line[4].token_type)
                    return math, errors
            if (found_line[5].token_type is enums.token_types.VAR):
                var1 = self.findAndReturnVar(found_vars, found_line[1].value)
                var2 = self.findAndReturnVar(found_vars, found_line[5].value)
                if var1 == False or var2 == False:
                    errors += [support.Error("unknown var", line_nr)]
                    return None, errors
                if var1 is not False and var2 is not False:
                    math = support.MathNode(var1, var2, line_nr, found_line[4].token_type)
                    return math, errors

    # getIfNode :: List[lexer.Token], List[support.VariableNode], int -> Tuple(support.IfNode, support.Error)
    def getIfNode(self, found_line : List[lexer.Token], found_vars : List[support.VariableNode], line_nr : int) -> Tuple[support.IfNode, support.Error]:
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
            errors += [support.Error("Variable to if on does not exist", line_nr)]
            return None, errors
        else:
            if found_line[4].token_type == enums.token_types.VAR:
                check_exist_condition = self.findAndReturnVar(found_vars, found_line[4].value)
                if check_exist_condition is False:
                    errors += [support.Error("condition does not exist", line_nr)]
                    return None, errors
                else:
                    condition = support.ConditionNode(check_exist_value, check_exist_condition, line_nr, found_line[3].token_type)
            elif found_line[4].token_type == enums.token_types.INT:
                condition = support.ConditionNode(check_exist_value, support.Node(found_line[4].value, line_nr, enums.token_types.INT), line_nr, found_line[3].token_type)
            elif found_line[4].token_type == enums.token_types.STRING:
                condition = support.ConditionNode(check_exist_value, support.Node(found_line[4].value, line_nr, enums.token_types.STRING), line_nr, found_line[3].token_type)

            if found_line[6].token_type == enums.token_types.VAR:
                check_exist_new_value = self.findAndReturnVar(found_vars, found_line[6].value)
                if check_exist_new_value is False:
                    errors += [support.Error("new value does not exist", line_nr)]
                    return None, errors
                else:
                    new_value = check_exist_new_value
            elif found_line[6].token_type == enums.token_types.INT:
                new_value = support.Node(found_line[6].value, line_nr, enums.token_types.INT)
            elif found_line[6].token_type == enums.token_types.STRING:
                new_value = support.Node(found_line[6].value, line_nr, enums.token_types.STRING)

            if len(found_line) == 9:
                if found_line[7].token_type == enums.token_types.ELSE:
                    if found_line[8].token_type == enums.token_types.VAR:
                        check_exist_new_value_false = self.findAndReturnVar(found_vars, found_line[8].value)
                        if check_exist_new_value_false is False:
                            errors += [support.Error("new value does not exist", line_nr)]
                            return None, errors
                        else:
                            new_value_false = check_exist_new_value_false
                    elif found_line[8].token_type == enums.token_types.INT:
                        new_value_false = support.Node(found_line[8].value, line_nr, enums.token_types.INT)
                    elif found_line[8].token_type == enums.token_types.STRING:
                        new_value_false = support.Node(found_line[8].value, line_nr, enums.token_types.STRING)
            
            var = support.IfNode(check_exist_value, condition, new_value, new_value_false, line_nr, enums.token_types.IF)
        return var, errors

    # getLine :: List[lexer.Token], List[lexer.Token] -> List[lexer.Token]
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

    # findAndReturnVar :: List[support.VariableNode], str -> Union(support.VariableNode, bool)
    def findAndReturnVar(self,  search_area : List[support.VariableNode], value_to_find : str ) -> Union[support.VariableNode, bool]:
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


