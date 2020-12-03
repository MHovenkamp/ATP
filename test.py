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
                print("l: ", line_number)
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
                variables_copy[copy_node.variable_name] = function_result
                return variables_copy[copy_node.variable_name], variables_copy
            elif copy_node.value.value == "INPUT":
                input_value = variables_copy["INPUT"]
                result, variables_copy = input_value.visit(variables_copy, function_body)
            elif copy_node.value.token_type == enums.token_types.VAR:
                value = variables_copy[copy_node.value.variable_name]
                variables_copy[copy_node.variable_name] = value
                result, variables_copy = value.visit(variables_copy, function_body)
            else:
                result, variables_copy = copy_node.value.visit(variables_copy, function_body)
            if type(result) is Error:
                return result, variables_copy
            variables_copy[copy_node.variable_name] = result
            return result, variables_copy
        
        elif copy_node.token_type == enums.token_types.OUTPUT:
            if copy_node.value.token_type == enums.token_types.VAR:
                print("copy_node ", copy_node.value)
                print(variables_copy)
                value = variables_copy[copy_node.value.variable_name]
                variables_copy[copy_node.variable_name] = value
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