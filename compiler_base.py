from typing import List, TypeVar, Union, Tuple

import support
import copy
import enums
import sys

# def getByteLengthBase( node: support.Node ) -> int:
#     if node.token_type == enums.token_types.STRING:
#         bytes = len(node.value) - 2 #because the node also contains the ""
#         if bytes % 4 != 0:
#             if bytes < 4:
#                 bytes = 4
#             else:
#                 bytes = (bytes // 4 ) * 4 + 4
#     elif node.token_type == enums.token_types.INT:
#         bits = int(node.value).bit_length()
#         bytes = bits // 8
#         if bits % 8 != 0:
#             bytes += 1
#         if bytes % 4 != 0:
#             bytes = (bytes // 4) * 4 + 4
#     return bytes

def getAmountOfVarsBytes( tree: List[support.Node], counter: int = 0,  ) -> int:
    if len(tree) == 0:
        return counter

    tree_copy = copy.copy(tree)
    counter_copy = copy.copy(counter)

    head, *tail = tree_copy
    if head.token_type == enums.token_types.VAR:
        # counter_copy += getByteLengthBase(head.value)
        counter_copy += 20 # Ik zet de grens op 1 variable op 20 bytes max
    return getAmountOfVarsBytes( tail, counter_copy)

def getNewStackSpotAddress( variable_memory_adresses : dict ) -> int:
    variable_memory_adresses_copy = copy.copy(variable_memory_adresses)

    values = variable_memory_adresses_copy.values()
    if values:
        highest_adress = max(values)
        new_adress = highest_adress[0] + highest_adress[1]
    else:
        new_adress = 0
    
    return new_adress

def startAssemblyCode(tree: List[support.Node], file_name : str) -> str:
    amount_of_bytes_to_reserve = getAmountOfVarsBytes(tree)
    
    start_txt = ".section .text\n.align 4\n.global " + file_name + "\n"

    start_txt += "\n" + file_name + ":"

    start_txt += "\nPUSH {R4,R5,R6,R7,LR}"
    start_txt += "\nMOV R6, SP"
    start_txt += "\nSUB SP, SP, #" + str(amount_of_bytes_to_reserve)        
    start_txt += "\nADD R7, SP, #0"

    return start_txt

def endAssemblyCode(word_List : List[str]) -> str:
    word_List_copy = copy.copy(word_List)
    end_txt = "\nend_of_program:"
    end_txt += "\nMOV SP, R6"
    end_txt += "\nPOP {R4,R5,R6,R7,PC}"
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
    print(word_List_copy)
    if value_type == enums.token_types.STRING:
        load_into_R0 = "\nLDR R0, " + value
        print_statement = "\nBL print_word"
    else:
        load_into_R0 = "\nMOV R0, " + value
        print_statement = "\nBL print_number"
    return load_into_R0 + print_statement, word_List_copy

def compilerBase( node: support.Node, word_List : List[str] ) -> str:
    word_List_copy = copy.copy(word_List)
    if node.token_type == enums.token_types.INT:
        return "#" + node.value, word_List_copy, enums.token_types.INT
    elif node.token_type == enums.token_types.STRING:
        bare_word = node.value[1:-1]
        if type(bare_word) == str:
            if "-" in bare_word:
                just_number = bare_word.lstrip("-")
                if just_number.isnumeric():
                    bare_word = int("-" + just_number)
                    return "#" + str(bare_word), word_List_copy, enums.token_types.INT
        if " " in bare_word:
            without_spaces = bare_word.replace(" ", "_")
            if without_spaces not in word_List_copy:
                word_List_copy.append(bare_word)
                return "=" + without_spaces, word_List_copy, enums.token_types.STRING
        elif node.value[1:-1] not in word_List_copy:
            word_List_copy.append(node.value[1:-1])
        return "=" + node.value[1:-1], word_List_copy, enums.token_types.STRING

def compilerVariable( node: support.VariableNode, variable_memory_adresses : dict, word_List : List[str], chosen_register: str = "3" ) -> Tuple[str, dict]:
    # set var into R3, also store in memory if not already stored
    variable_memory_adresses_copy = copy.copy(variable_memory_adresses)
    node_copy = copy.copy(node)
    word_List_copy = copy.copy(word_List)

    assembly_string = ""
    chosen_register_copy = str(chosen_register)

    if node_copy.variable_name in variable_memory_adresses_copy:
        load_value = "\nLDR R" + chosen_register_copy + ",[R7, #" + variable_memory_adresses_copy[node.variable_name][0] + "]"
        assembly_string += load_value
        if node_copy.token_type == enums.token_types.OUT:
            load_into_R0 = "\nMOV R0, R" + chosen_register_copy
    else: #var not known or OUT
        if node_copy.token_type == enums.token_types.OUT:
            if node_copy.value.node_type == enums.node_types.VAR:
                load_value = "\nLDR R" + chosen_register_copy + ",[R7, #" + str(variable_memory_adresses_copy[node.value.variable_name][0]) + "]"
                load_into_R0 = "\nMOV R0, R" + chosen_register_copy
                base_type = variable_memory_adresses_copy[node.value.variable_name][2]
                if base_type == enums.token_types.STRING:
                    print_statement = "\nBL print_word"
                else:
                    print_statement = "\nBL print_number"
                assembly_string += load_value + load_into_R0 + print_statement
            elif node_copy.value.node_type == enums.node_types.BASE:
                string, word_List_copy = printValueBase(node_copy, word_List_copy)
                assembly_string += string
        elif node_copy.token_type == enums.token_types.ERR:
            value_without_spaces = node_copy.value[1:-1].replace(" ", "_")
            load_into_R0 = "\nLDR R0, =" + value_without_spaces
            word_List_copy.append(node_copy.value[1:-1])
            print_statement = "\nBL print_word"
            end_program = "\nB end_of_program"
            assembly_string += load_into_R0 + print_statement + end_program
        else: #var not known
            if node_copy.value.node_type == enums.node_types.BASE:
                adress = getNewStackSpotAddress( variable_memory_adresses_copy)
                adress = str(adress)
                value, word_List_copy, value_type = compilerBase(node_copy.value, word_List_copy)
                if value_type == enums.token_types.STRING:
                    load_into_R0 = "\nLDR R" + chosen_register_copy + ", " + value
                else:
                    load_into_R0 = "\nMOV R" + chosen_register_copy + ", " + value
                store = "\nSTR R" + chosen_register_copy + ",[R7,#" + adress + "]" 
                assembly_string += load_into_R0 + store
                variable_memory_adresses_copy[node_copy.variable_name] = [int(adress), 20, node_copy.value.token_type]
            elif node_copy.value.node_type == enums.node_types.VAR:
                load_var_value = "\nLDR R" + chosen_register_copy + ",[R7,#" + str(variable_memory_adresses[node.value.variable_name][0]) + "]"
                new_address = getNewStackSpotAddress(variable_memory_adresses_copy)
                new_address = str(new_address)
                restore_under_new_var_name = "\nSTR R" + chosen_register_copy + ",[R7,#" + new_address + "]" 
                assembly_string += load_var_value + restore_under_new_var_name
                base_type = variable_memory_adresses[node.value.variable_name][2]
                variable_memory_adresses_copy[node_copy.variable_name] = [int(new_address), 20, base_type ]

    return assembly_string, variable_memory_adresses_copy, word_List_copy

def compilerMath( node: support.MathNode, variable_memory_adresses : dict, word_List : List[str], chosen_register: str = "3" ) -> Tuple[str, dict]:
    node_copy = copy.copy(node)
    variable_memory_adresses_copy = copy.copy(variable_memory_adresses)
    word_List_copy = copy.copy(word_List)

    #load var into R3
    command_start = "\nLDR R3,[R7,#" + str(variable_memory_adresses_copy[node_copy.value.variable_name][0]) + "]"
    # check if rhs is var or base object
    if node_copy.token_type == enums.token_types.ADD:
        operator = "\nADD"
    elif node_copy.token_type == enums.token_types.SUB:
        operator = "\nSUB"
    elif node_copy.token_type == enums.token_types.MUL:
        operator = "\nMUL"
    elif node_copy.token_type == enums.token_types.DIV:
        operator = "\nUDIV" 

    if node_copy.rhs.node_type == enums.node_types.BASE:
        value, word_List_copy, value_type = compilerBase(node_copy.rhs.value, word_List_copy)
        if value_type == enums.token_types.INT:
            command_start += operator + " R3 , R3, " + value
    elif node_copy.rhs.node_type == enums.node_types.VAR:
        #load rhs into R2
        load_var = "\nLDR R2,[R7,#" + str(variable_memory_adresses[node_copy.rhs.variable_name][0]) + "]"
        command_start += load_var + operator + " R3, R3, R2"
    
    #store new result
    store = "\nSTR R3, [R7,#" + str(variable_memory_adresses_copy[node_copy.value.variable_name][0]) +"]"
    command_start += store
    variable_memory_adresses_copy[node_copy.value.variable_name][1] = getByteLengthBase(node_copy.value.value)

    if chosen_register != "3":
        command_start += "\nMOV R" + chosen_register + ", R3"
    return command_start, variable_memory_adresses_copy, word_List_copy

def compilerIf( node: support.IfNode, variable_memory_adresses : dict, word_List : List[str] ) -> str:
    node_copy = copy.copy( node )
    condition_node_copy = node_copy.condition
    variable_memory_adresses_copy = copy.copy(variable_memory_adresses)
    word_List_copy = copy.copy(word_List)

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
    load_var1 = "\nLDR R3,[R7,#" + str(variable_memory_adresses[node_copy.value.variable_name][0]) + "]"
    if condition_node_copy.condition.node_type == enums.node_types.VAR:
        load_var2 = "\nLDR R3,[R7,#" + str(variable_memory_adresses[condition_node_copy.condition.variable_name][0]) + "]"
    else:
        print(condition_node_copy.condition)
        value, word_List_copy, value_type = compilerBase(condition_node_copy.condition, word_List_copy)
        if value_type == enums.token_types.STRING:
            load_var2 = "\nLDR R2, " + value
        else:
            load_var2 = "\nMOV R2, " + value
    compare = "\nCMP R3,R2"
    action = operator + " line_" + str(node_copy.line_nr) + "_true"
    if node_copy.new_value_false.node_type == enums.node_types.BASE:
        value, word_List_copy, value_type = compilerBase(node_copy.new_value_false, word_List_copy)
        if value_type == enums.token_types.STRING:
            change_org_var = "\nLDR R3, " + value
        else:
            change_org_var = "\nMOV R3, " + value
    restore_var = "\nSTR R3, [R7,#" + str(variable_memory_adresses_copy[node_copy.value.variable_name][0]) +"]"
    skip_true = "\nB line_" + str(node_copy.line_nr+1)

    new_line = "\nline_" + str(node_copy.line_nr) + "_true:"
    if node_copy.new_value_true.node_type == enums.node_types.BASE:
        value, word_List_copy, value_type = compilerBase(node_copy.new_value_true, word_List_copy)
        if value_type == enums.token_types.STRING:
            change_org_var2 = "\nLDR R3, " + value
        else:
            change_org_var2 = "\nMOV R3, " + value

    restore_var = "\nSTR R3, [R7,#" + str(variable_memory_adresses_copy[node_copy.value.variable_name][0]) +"]"
    
    old_addres = str(variable_memory_adresses_copy[node_copy.value.variable_name][0])
    variable_memory_adresses_copy[node_copy.value.variable_name] = [old_addres, 20, enums.token_types.STRING]

    asm_string = load_var1 + load_var2 + compare + action + change_org_var + restore_var + skip_true
    asm_string += new_line + change_org_var2 + restore_var

    return asm_string, variable_memory_adresses_copy, word_List_copy

# def compilerFunction( node : support.FunctionNode, variable_memory_adresses : dict) ->str:

# def compilerFunctionCall( node : support.FunctionCall, variable_memory_adresses : dict ) ->str:
    
    
