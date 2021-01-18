from typing import List, TypeVar, Union, Tuple

import support
import copy
import enums
import sys

def getByteLengthBase( node: support.Node ) -> int:
    if node.token_type == enums.token_types.STRING:
        bytes = len(node.value) - 2 #because the node also contains the ""
        if bytes % 4 != 0:
            if bytes < 4:
                bytes = 4
            else:
                bytes = (bytes // 4 ) * 4 + 4
    elif node.token_type == enums.token_types.INT:
        bits = int(node.value).bit_length()
        bytes = bits // 8
        if bits % 8 != 0:
            bytes += 1
        if bytes % 4 != 0:
            bytes = (bytes // 4) * 4 + 4
    return bytes

def getAmountOfVarsBytes( tree: List[support.Node], counter: int = 0 ) -> int:
    if len(tree) == 0:
        return counter

    tree_copy = copy.copy(tree)
    counter_copy = copy.copy(counter)

    head, *tail = tree_copy
    if head.token_type == enums.token_types.VAR:
        counter_copy += getByteLengthBase(head.value)
    return getAmountOfVarsBytes( tail, counter_copy)

def getNewStackSpotAddress( node: support.Node, variable_memory_adresses : dict ) -> int:
    variable_memory_adresses_copy = copy.copy(variable_memory_adresses)

    values = variable_memory_adresses_copy.values()
    if values:
        highest_adress = max(values)
        new_adress = highest_adress[0] + highest_adress[1]
    else:
        new_adress = 0
    
    return new_adress

def start_assembly_code(tree: List[support.Node], file_name : str) -> str:
    amount_of_bytes_to_reserve = getAmountOfVarsBytes(tree)
    
    start_txt = ".section .text\n.align 4\n.global " + file_name + "\n"

    start_txt += "\nPUSH {R7, lr}"
    start_txt += "\nSUB SP, SP, #" + str(amount_of_bytes_to_reserve)        
    start_txt += "\nADD R7, SP, #0"

    return start_txt

def compilerBase( node: support.Node ) -> str:
    if node.token_type == enums.token_types.INT:
        return "#" + node.value
    elif node.token_type == enums.token_types.STRING:
        return node.value

def compilerVariable( node: support.VariableNode, variable_memory_adresses : dict, chosen_register: str = "3" ) -> Tuple[str, dict]:
    # set var into R3, also store in memory if not already stored
    variable_memory_adresses_copy = copy.copy(variable_memory_adresses)
    node_copy = copy.copy(node)
    assembly_string = ""
    chosen_register_copy = str(chosen_register)

    if node.variable_name in variable_memory_adresses_copy:
        load_value = "\n LDR R" + chosen_register_copy + ",[R7, #" + variable_memory_adresses_copy[node.variable_name][0] + "]"
        assembly_string += load_value
    else:
        adress = getNewStackSpotAddress( node_copy, variable_memory_adresses_copy)
        adress = str(adress)
        value_to_reg = "\nMOV R" + chosen_register_copy + " " + compilerBase(node_copy.value)
        store = "\nSTR R" + chosen_register_copy + ",[R7,#" + adress + "]" 
        assembly_string += value_to_reg + store
        variable_memory_adresses_copy[node_copy.variable_name] = [int(adress), getByteLengthBase(node_copy.value)]

    return assembly_string, variable_memory_adresses_copy

def compilerMath( node: support.MathNode, variable_memory_adresses : dict, chosen_register: str = "3" ) -> Tuple[str, dict]:
    node_copy = copy.copy(node)
    variable_memory_adresses_copy = copy.copy(variable_memory_adresses)

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
        #command
        command_start += operator + " R3 , R3, " + compilerBase(node_copy.rhs.value)
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
    return command_start, variable_memory_adresses_copy

# def compilerFunction( node : support.FunctionNode, variable_memory_adresses : dict) ->str:

# def compilerFunctionCall( node : support.FunctionCall, variable_memory_adresses : dict ) ->str:
    
    
