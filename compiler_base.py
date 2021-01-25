from typing import List, TypeVar, Union, Tuple

import support
import copy
import enums
import sys

def getAmountOfVarsBytes( tree: List[support.Node], counter: int = 0  ) -> int:
    if len(tree) == 0:
        return counter

    tree_copy = copy.copy(tree)
    counter_copy = copy.copy(counter)

    head, *tail = tree_copy
    if head.token_type == enums.token_types.VAR:
        counter_copy += 8 # Ik zet de grens op 1 variable op 8 bytes max
    return getAmountOfVarsBytes(tail, counter_copy)

def getNewStackSpotAddress( variable_memory_adresses : dict, name :str ) -> int:
    variable_memory_adresses_copy = copy.copy(variable_memory_adresses)

    if name in variable_memory_adresses_copy.keys():
        return variable_memory_adresses_copy[name][0]

    values = variable_memory_adresses_copy.values()
    if values:
        highest_adress = max(values)
        new_adress = highest_adress[0] + highest_adress[1]
    else:
        new_adress = 0
    
    return new_adress

def getAmountOfVarsBytesFunction( tree: List[support.Node], counter: int = 0 ):
    tree_copy = copy.copy(tree)
    counter_copy = copy.copy(counter)

    if len(tree_copy) ==0:
        return counter_copy

    head, *tail = tree_copy

    counter_copy += getAmountOfVarsBytes(head.commands)

    return getAmountOfVarsBytesFunction( tail, counter_copy)

def startAssemblyCode(tree: List[support.Node], found_funcs : dict, file_name : str) -> str:
    amount_of_bytes_to_reserve = getAmountOfVarsBytes(tree)
    amount_of_bytes_to_reserve += getAmountOfVarsBytesFunction(list(found_funcs.values()))
    
    start_txt = ".section .text\n.align 4\n.global " + file_name + "\n"

    return start_txt, amount_of_bytes_to_reserve

def endAssemblyCode(word_List : List[str], line_numbers : List[int]) -> str:
    word_List_copy = copy.copy(word_List)
    end_txt = "\nB end_of_program"
    end_txt = "\n\nend_of_program:"
    end_txt += "\nMOV SP, R6"
    end_txt += "\nPOP {R4,R5,R6,R7,PC}"
    end_txt += "\n" + createLookupTable(line_numbers)
    end_txt += addWords(word_List_copy)

    return end_txt

def addWords(word_List : List[str], asm_string : str = "") -> str:
    if len(word_List) == 0:
        return asm_string
    
    word_List_copy = copy.copy(word_List)
    asm_string_copy = copy.copy(asm_string)
    
    if asm_string == "":
        asm_string_copy += "\n\n.data"    


    head, *tail = word_List_copy
    if " " in head:
        asm_string_copy += "\n" + head.replace(" ", "_") + ":"
        asm_string_copy += "\t.asciz \"" + head + "\""
    else:
        asm_string_copy += "\n" + head + ":"
        asm_string_copy += "\t.asciz \"" + head + "\""

    return addWords( tail, asm_string_copy)

def printValueBase( node: support.Node, word_List : List[str] ) -> str:
    value, word_List_copy, value_type = compilerBase(node.value, word_List)
    if value_type == enums.token_types.STRING:
        load_into_R0 = "\nLDR R0, " + value
        print_statement = "\nBL print_word"
    else:
        load_into_R0 = "\nMOV R0, " + value
        print_statement = "\nBL print_number"
    return load_into_R0 + print_statement, word_List_copy

def getFoundFuncsOffsetDict( found_funcs : List[str], main_fileName : str, new_dict : dict = {}, counter : int = 0 ) -> dict:
    found_funcs_copy = copy.copy(found_funcs)
    new_dict_copy = copy.copy(new_dict)
    counter_copy = copy.copy(counter)
    if len( new_dict_copy ) == 0:
        new_dict_copy[main_fileName] = counter_copy

    if len(found_funcs_copy) == 0:
        return new_dict

    head, *tail = found_funcs_copy
    if(type(head) is not str):
        new_dict_copy[(head.value)] = counter
    else:
        new_dict_copy[(head)] = counter
    return getFoundFuncsOffsetDict( tail, main_fileName ,new_dict_copy, counter_copy+100)

def createLookupTable( line_numbers : List[str], asm_string : str = "\nlookUpTable:" ):
    line_numbers_copy = copy.copy(line_numbers)
    asm_string_copy = copy.copy(asm_string)

    if len(line_numbers_copy) == 0:
        return asm_string_copy

    head, *tail = line_numbers_copy

    asm_string_copy += "\nCMP R0, #" + str(head)
    asm_string_copy += "\nBEQ _line_" + str(head)
    return createLookupTable(tail, asm_string_copy)

list_types = TypeVar(support.Node, support.VariableNode, support.MathNode, support.Error)
def compile( main_func_name : str, ast: List[list_types], found_funcs : dict, asm_string : str = "", variable_memory_adresses : dict = {}, word_List : List[str] = [], func_offset : dict = {}, line_numbers : List[int] = []):

    if len(ast) == 0:
        return asm_string, variable_memory_adresses, word_List, line_numbers

    ast_copy = copy.copy(ast)
    found_funcs_copy = copy.copy(found_funcs)
    variable_memory_adresses_copy = copy.copy(variable_memory_adresses)
    word_List_copy = copy.copy(word_List)
    line_numbers_copy = copy.copy(line_numbers)

    if asm_string == "":
        asm_string_copy, amount_of_bytes_to_reserve =  startAssemblyCode( ast_copy, found_funcs_copy, main_func_name) 
        func_offset = getFoundFuncsOffsetDict( ["code"]+ list(found_funcs.values()), main_func_name )
        asm_string_copy, variable_memory_adresses_copy, word_List_copy, line_numbers_copy =  compileAlFunctions(list(found_funcs.values()), main_func_name, found_funcs_copy, variable_memory_adresses_copy,func_offset, word_List_copy, asm_string_copy)    
        asm_string_copy += "\n" + main_func_name + ":"  
        asm_string_copy += "\nPUSH {R4,R5,R6,R7,LR}"
        asm_string_copy += "\nMOV R6, SP"
        asm_string_copy += "\nSUB SP, SP, #" + str(amount_of_bytes_to_reserve)        
        asm_string_copy += "\nADD R7, SP, #0\n"
    else:
        asm_string_copy = copy.copy(asm_string)

    head, *tail = ast_copy

    line_number = func_offset[main_func_name] + head.line_nr

    line_numbers_copy.append(line_number)
    asm_string_copy += "\n_line_"+str(line_number)+":"

    if head.node_type == enums.node_types.VAR:
        string, variable_memory_adresses_copy, word_List_copy = compilerVariable(head, main_func_name, variable_memory_adresses_copy, func_offset, word_List_copy)
        asm_string_copy += string
    
    elif head.node_type == enums.node_types.INPUT:
        if head.variable_name in variable_memory_adresses_copy.keys():
            string, variable_memory_adresses_copy, word_List_copy = compilerVariable(head, main_func_name, variable_memory_adresses_copy, func_offset, word_List_copy)
        else:
            string, variable_memory_adresses_copy, word_List_copy = compilerFunctionInput(head, main_func_name, variable_memory_adresses_copy, word_List_copy)
        asm_string_copy += string

    elif head.node_type == enums.node_types.MATH:
        string, variable_memory_adresses_copy, word_List_copy = compilerMath(head, main_func_name, variable_memory_adresses_copy, word_List_copy)
        asm_string_copy += string

    elif head.node_type == enums.node_types.IF:
        string, variable_memory_adresses_copy, word_List_copy = compilerIf(head, main_func_name, variable_memory_adresses_copy, word_List_copy, func_offset)
        asm_string_copy += string

    elif head.node_type == enums.node_types.FUNCTION_CALL:
        string, variable_memory_adresses_copy, word_List_copy = compilerFunctionCall(head, main_func_name, found_funcs, variable_memory_adresses_copy, word_List_copy)
        asm_string_copy += string

    return compile( main_func_name, tail, found_funcs_copy, asm_string_copy, variable_memory_adresses_copy, word_List_copy, func_offset, line_numbers_copy)



def compilerBase( node: support.Node, word_List : List[str] ) -> str:
    word_List_copy = copy.copy(word_List)
    if node.token_type == enums.token_types.INT:
        if int(node.value) < 0:
            string = "#" + str(int(node.value)*-1) 
            string += "\nMOV R4, #0"
            string +="\nSUB R3, R4, R3"
            return string, word_List_copy, enums.token_types.INT
        else:
            return "#" + node.value, word_List_copy, enums.token_types.INT
    elif node.token_type == enums.token_types.STRING:
        bare_word = node.value[1:-1]
        if " " in bare_word:
            without_spaces = bare_word.replace(" ", "_")
            if without_spaces not in word_List_copy:
                word_List_copy.append(bare_word)
                return "=" + without_spaces, word_List_copy, enums.token_types.STRING
        elif node.value[1:-1] not in word_List_copy:
            word_List_copy.append(node.value[1:-1])
        return "=" + node.value[1:-1], word_List_copy, enums.token_types.STRING

def compilerVariable( node: support.VariableNode, main_func_name : str, variable_memory_adresses : dict, func_offset : dict, word_List : List[str], chosen_register: str = "3" ) -> Tuple[str, dict]:
    # set var into R3, also store in memory if not already stored
    variable_memory_adresses_copy = copy.copy(variable_memory_adresses)
    node_copy = copy.copy(node)
    word_List_copy = copy.copy(word_List)
    main_func_name_copy = copy.copy(main_func_name)

    assembly_string = ""
    chosen_register_copy = str(chosen_register)

    # if main_func_name + node_copy.variable_name in variable_memory_adresses_copy and node_copy.node_type != enums.node_types.INPUT:


    #     load_value = "\nLDR R" + chosen_register_copy + ",[R7, #" + str(variable_memory_adresses_copy[main_func_name +node.variable_name][0]) + "]"
    #     assembly_string += load_value
    #     if node_copy.token_type == enums.token_types.OUT:
    #         load_into_R0 = "\nMOV R0, R" + chosen_register_copy
    # else: #var not known or OUT
    if node_copy.token_type == enums.token_types.OUT:
        if node_copy.value.node_type == enums.node_types.VAR:
            load_value = "\nLDR R" + chosen_register_copy + ",[R7, #" + str(variable_memory_adresses_copy[main_func_name + node.value.variable_name][0]) + "]"
            load_into_R0 = "\nMOV R0, R" + chosen_register_copy
            base_type = variable_memory_adresses_copy[main_func_name +node.value.variable_name][2]
            if base_type == enums.token_types.STRING:
                print_statement = "\nBL print_word"
            else:
                print_statement = "\nBL print_number"
            assembly_string += load_value + load_into_R0 + print_statement
        elif node_copy.value.node_type == enums.node_types.BASE:
            string, word_List_copy = printValueBase(node_copy, word_List_copy)
            assembly_string += string
        elif node_copy.value.node_type == enums.node_types.INPUT:
            load_value = "\nLDR R" + chosen_register_copy + ",[R7,#" + str(variable_memory_adresses_copy[main_func_name +node.value.variable_name][0]) + "]"
            load_into_R0 = "\nMOV R0, R" + chosen_register_copy
            base_type = variable_memory_adresses_copy[main_func_name +node.value.variable_name][2]
            if base_type == enums.token_types.STRING:
                print_statement = "\nBL print_word"
            else:
                print_statement = "\nBL print_number"
            assembly_string += load_value + load_into_R0 + print_statement
    elif node_copy.token_type == enums.token_types.ERR:
        value_without_spaces = node_copy.value[1:-1].replace(" ", "_")
        load_into_R0 = "\nLDR R0, =" + value_without_spaces
        word_List_copy.append(node_copy.value[1:-1])
        print_statement = "\nBL print_word"
        end_program = "\nB end_of_program"
        assembly_string += load_into_R0 + print_statement + end_program
    elif node_copy.token_type == enums.token_types.DECLARE:
        return assembly_string, variable_memory_adresses_copy, word_List_copy
    elif node_copy.token_type == enums.token_types.OUTPUT:
        if node_copy.value.token_type == enums.token_types.VAR:
            load_into_R0 = "\nLDR R0, [R7,#" + str(variable_memory_adresses_copy[main_func_name +node_copy.value.variable_name][0]) +"]"
        else:
            value, word_List_copy, value_type = compilerBase(node_copy.value, word_List_copy)
            if value_type == enums.token_types.STRING:
                load_into_R0 = "\nLDR R" + chosen_register_copy + ", " + value
            else:
                load_into_R0 = "\nMOV R" + chosen_register_copy + ", " + value
        assembly_string += load_into_R0
        return assembly_string, variable_memory_adresses_copy, word_List_copy
    elif node_copy.token_type == enums.token_types.LINE:
        if node_copy.value.token_type == enums.token_types.INT:
            line_nr = node_copy.line_nr + int(node_copy.value.value) + func_offset[main_func_name_copy]
            branch = "\nB _line_" + str(line_nr)
            assembly_string += branch
            return assembly_string, variable_memory_adresses_copy, word_List_copy
        elif node_copy.value.token_type == enums.token_types.VAR:
            load_into_R0 = "\nLDR R0 ,[R7, #" + str(variable_memory_adresses_copy[main_func_name +node.value.variable_name][0]) + "]"
            load_line_number = "\nADD R0, R0" + ", #" + str(node_copy.line_nr)
            load_line_number2 = "\nADD R0, R0, #" + str(func_offset[main_func_name_copy])
            branch = "\nB lookUpTable"
            assembly_string += load_into_R0 + load_line_number + load_line_number2 +branch
            return assembly_string, variable_memory_adresses_copy, word_List_copy
    else: #var not known
        if node_copy.value.node_type == enums.node_types.BASE and node_copy.value.token_type != enums.token_types.INPUT:
            adress = getNewStackSpotAddress( variable_memory_adresses_copy, main_func_name + node_copy.variable_name)
            adress = str(adress)
            value, word_List_copy, value_type = compilerBase(node_copy.value, word_List_copy)
            if value_type == enums.token_types.STRING:
                load_into_R0 = "\nLDR R" + chosen_register_copy + ", " + value
            else:
                load_into_R0 = "\nMOV R" + chosen_register_copy + ", " + value
            store = "\nSTR R" + chosen_register_copy + ",[R7,#" + adress + "]" 
            assembly_string += load_into_R0 + store
            variable_memory_adresses_copy[main_func_name + node_copy.variable_name] = [int(adress), 8, node_copy.value.token_type]
        elif node_copy.value.node_type == enums.node_types.VAR or node_copy.value.node_type == enums.node_types.INPUT:
            load_var_value = "\nLDR R" + chosen_register_copy + ",[R7,#" + str(variable_memory_adresses[main_func_name+ node.value.variable_name][0]) + "]"
            new_address = getNewStackSpotAddress(variable_memory_adresses_copy, main_func_name + node_copy.variable_name)
            new_address = str(new_address)
            restore_under_new_var_name = "\nSTR R" + chosen_register_copy + ",[R7,#" + new_address + "]" 
            assembly_string += load_var_value + restore_under_new_var_name
            base_type = variable_memory_adresses[main_func_name+node.value.variable_name][2]
            variable_memory_adresses_copy[main_func_name +node_copy.variable_name] = [int(new_address), 8, base_type ]

    return assembly_string, variable_memory_adresses_copy, word_List_copy

def compilerMath( node: support.MathNode, main_func_name : str, variable_memory_adresses : dict, word_List : List[str], chosen_register: str = "3" ) -> Tuple[str, dict]:
    node_copy = copy.copy(node)
    variable_memory_adresses_copy = copy.copy(variable_memory_adresses)
    word_List_copy = copy.copy(word_List)
    main_func_name_copy = copy.copy(main_func_name)


    #load var into R3
    command_start = "\nLDR R3,[R7,#" + str(variable_memory_adresses_copy[main_func_name +node_copy.value.variable_name][0]) + "]"
    # check if rhs is var or base object
    if node_copy.token_type == enums.token_types.ADD:
        operator = "\nADD"
    elif node_copy.token_type == enums.token_types.SUB:
        operator = "\nSUB"
    elif node_copy.token_type == enums.token_types.MUL:
        operator = "\nMUL"
    elif node_copy.token_type == enums.token_types.DIV:
        load_into_R0 = "\nLDR R0,[R7,#" + str(variable_memory_adresses[main_func_name+node_copy.value.variable_name][0]) + "]"
        if node_copy.rhs.node_type == enums.node_types.BASE:
            value, word_List_copy, value_type =  compilerBase(node_copy.rhs, word_List_copy)
            if value_type == enums.token_types.STRING:
                load_into_R1 = "\nLDR R1, " + value
            else:
                load_into_R1 = "\nMOV R1, " + value
        else:
            load_into_R1 = "\nLDR R1,[R7,#" + str(variable_memory_adresses[main_func_name+node_copy.rhs.variable_name][0]) + "]"
        link_to_divide = "\nBL divide"
        restore_Result = "\nSTR R0,[R7,#" + str(variable_memory_adresses[main_func_name+node_copy.value.variable_name][0]) + "]"
        message = load_into_R0 + load_into_R1 + link_to_divide + restore_Result
        return message, variable_memory_adresses_copy, word_List_copy

    if node_copy.rhs.node_type == enums.node_types.BASE:
        value, word_List_copy, value_type = compilerBase(node_copy.rhs, word_List_copy)
        if value_type == enums.token_types.INT:
            command_start += operator + " R3 , R3, " + value
    elif node_copy.rhs.node_type == enums.node_types.VAR or node_copy.rhs.node_type == enums.node_types.INPUT:
        #load rhs into R2
        load_var = "\nLDR R2,[R7,#" + str(variable_memory_adresses[main_func_name+node_copy.rhs.variable_name][0]) + "]"
        command_start += load_var + operator + " R3, R3, R2"
    
    #store new result
    store = "\nSTR R3, [R7,#" + str(variable_memory_adresses_copy[main_func_name +node_copy.value.variable_name][0]) +"]"
    command_start += store
    variable_memory_adresses_copy[main_func_name +node_copy.value.variable_name][2] = enums.token_types.INT

    if chosen_register != "3":
        command_start += "\nMOV R" + chosen_register + ", R3"
    return command_start, variable_memory_adresses_copy, word_List_copy

def compilerIf( node: support.IfNode, main_func_name : str, variable_memory_adresses : dict, word_List : List[str], func_offset : dict ) -> str:
    node_copy = copy.copy( node )
    condition_node_copy = node_copy.condition
    variable_memory_adresses_copy = copy.copy(variable_memory_adresses)
    word_List_copy = copy.copy(word_List)
    main_func_name_copy = copy.copy(main_func_name)

    if condition_node_copy.token_type == enums.token_types.EQUAL:
        operator = "\nBEQ"
    elif condition_node_copy.token_type == enums.token_types.NOTEQUAL:
        operator = "\nBNE"
    elif condition_node_copy.token_type == enums.token_types.EQUALGREATER:
        operator = "\nBGE"
    elif condition_node_copy.token_type == enums.token_types.EQUALSMALLER:
        operator = "\nBLE"
    elif condition_node_copy.token_type == enums.token_types.GREATER:
        operator = "\nBHI"
    elif condition_node_copy.token_type == enums.token_types.SMALLER:
        operator = "\nBLT"
    load_var1 = "\nLDR R3,[R7,#" + str(variable_memory_adresses[main_func_name+node_copy.value.variable_name][0]) + "]"
    if condition_node_copy.condition.node_type == enums.node_types.VAR:
        load_var2 = "\nLDR R3,[R7,#" + str(variable_memory_adresses[condition_node_copy.condition.variable_name][0]) + "]"
    else:
        value, word_List_copy, value_type = compilerBase(condition_node_copy.condition, word_List_copy)
        if value_type == enums.token_types.STRING:
            load_var2 = "\nLDR R2, " + value
        else:
            load_var2 = "\nMOV R2, " + value
    compare = "\nCMP R3,R2"
    action = operator +" " +main_func_name+ "_line_" + str(node_copy.line_nr) + "_true"
    if node_copy.new_value_false.node_type == enums.node_types.BASE:
        value, word_List_copy, value_type = compilerBase(node_copy.new_value_false, word_List_copy)
        if value_type == enums.token_types.STRING:
            change_org_var = "\nLDR R3, " + value
        else:
            change_org_var = "\nMOV R3, " + value
    restore_var = "\nSTR R3, [R7,#" + str(variable_memory_adresses_copy[main_func_name +node_copy.value.variable_name][0]) +"]"
    skip_true = "\nB "+ "_line_" + str(node_copy.line_nr+1 + func_offset[main_func_name])

    new_line = "\n" + main_func_name_copy + "_line_" + str(node_copy.line_nr) + "_true:"
    if node_copy.new_value_true.node_type == enums.node_types.BASE:
        value, word_List_copy, value_type = compilerBase(node_copy.new_value_true, word_List_copy)
        if value_type == enums.token_types.STRING:
            change_org_var2 = "\nLDR R3, " + value
        else:
            change_org_var2 = "\nMOV R3, " + value

    restore_var = "\nSTR R3, [R7,#" + str(variable_memory_adresses_copy[main_func_name +node_copy.value.variable_name][0]) +"]"
    
    old_addres = variable_memory_adresses_copy[main_func_name + node_copy.value.variable_name][0]
    variable_memory_adresses_copy[main_func_name + node_copy.value.variable_name] = [old_addres, 8, enums.token_types.STRING]

    asm_string = load_var1 + load_var2 + compare + action + change_org_var + restore_var + skip_true
    asm_string += new_line + change_org_var2 + restore_var

    return asm_string, variable_memory_adresses_copy, word_List_copy

def compilerFunctionCall( node: support.FunctionCall, main_func_name : str, found_funcs : dict, variable_memory_adresses : dict, word_List : List[str]):
    # link to function and then put RO value into memory under variabel name
    node_copy = copy.copy(node)
    main_func_name_copy = copy.copy(main_func_name)
    variable_memory_adresses_copy = copy.copy(variable_memory_adresses)
    word_List_copy = copy.copy(word_List)
    found_funcs_copy = copy.copy(found_funcs)

    if node_copy.input.node_type == enums.node_types.BASE:
        value, word_List_copy, value_type = compilerBase(node_copy.input, word_List_copy)
        give_input = "\nMOV R0, " + value
    else:
        give_input = "\nLDR R0,[R7,#" + str(variable_memory_adresses_copy[main_func_name + node_copy.input.variable_name][0]) + "]"
    link_to_function = "\nBL " + node_copy.value 
    new_address = getNewStackSpotAddress( variable_memory_adresses_copy,  main_func_name + node_copy.output.variable_name )
    save_var_func_result = "\nSTR R0, [R7,#" + str(new_address) + "]"
    variable_memory_adresses_copy[main_func_name +node_copy.output.variable_name] = [new_address, 8, enums.token_types.INT]
    return give_input+link_to_function+save_var_func_result, variable_memory_adresses_copy, word_List_copy

def compileAlFunctions( found_func : List[support.FunctionNode], main_func_name : str, found_funcs : dict, variable_memory_adresses : dict, func_offset :dict, word_List : List[str], asm_string: str = "", line_numbers : List[str] = []) -> str:
    found_func_copy = copy.copy(found_func)
    main_func_name_copy = copy.copy(main_func_name)
    variable_memory_adresses_copy = copy.copy(variable_memory_adresses)
    word_List_copy = copy.copy(word_List)
    asm_string_copy = copy.copy(asm_string)
    found_funcs_copy = copy.copy(found_funcs)
    line_numbers_copy = copy.copy(line_numbers)

    if len(found_func) == 0:
        return asm_string_copy, variable_memory_adresses, word_List_copy, line_numbers_copy

    head, *tail = found_func
    asm_string_copy += "\n\n" + head.value + ":"
    asm_string_copy += "\nPUSH {LR}"
   
    add_string, variable_memory_adresses_copy, word_List_copy, line_numbers_copy = compilerFunction(head, head.value, found_funcs_copy, variable_memory_adresses_copy, func_offset, word_List_copy, asm_string_copy)

    add_string += "\nPOP {PC}\n"

    return compileAlFunctions(tail, main_func_name_copy, found_funcs_copy, variable_memory_adresses_copy, func_offset, word_List_copy, add_string, line_numbers_copy)
 
def compilerFunction( node: support.FunctionNode, main_func_name : str, found_funcs: dict, variable_memory_adresses : dict, func_offset : dict, word_List : List[str], asm_string: str = "") ->str:
    node_copy = copy.copy(node)
    main_func_name_copy = copy.copy(main_func_name)
    variable_memory_adresses_copy = copy.copy(variable_memory_adresses)
    word_List_copy = copy.copy(word_List)
    found_funcs_copy = copy.copy(found_funcs)

    string, variable_memory_adresses_copy, word_List_copy, line_numbers_copy =  compile(node_copy.value, node_copy.commands, found_funcs_copy, asm_string, variable_memory_adresses_copy, word_List_copy, func_offset)

    return string, variable_memory_adresses_copy, word_List_copy, line_numbers_copy
    
def compilerFunctionInput(node: support.VariableNode, main_func_name : str, variable_memory_adresses : dict, word_List : List[str]):
    variable_memory_adresses_copy = copy.copy(variable_memory_adresses)
    word_List_copy = copy.copy(word_List)

    new_address = getNewStackSpotAddress( variable_memory_adresses_copy,  main_func_name + node.variable_name)
    store_input_value = "\nSTR R0, [R7,#" + str(new_address) + "]"
    variable_memory_adresses_copy[main_func_name + node.variable_name] = [new_address, 8, enums.token_types.INT]

    return store_input_value, variable_memory_adresses_copy, word_List_copy
    