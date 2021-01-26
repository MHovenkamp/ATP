from typing import List, TypeVar, Union, Tuple

import support
import copy
import enums
import sys

# getAmountOfVarsBytes :: List[support.Node], int -> int
def getAmountOfVarsBytes( tree: List[support.Node], counter: int = 0  ) -> int:
    """gets the amount of bytes to reserve on the stack for a function body

    Args:
        tree (List[support.Node]): ast of function body
        counter (int, optional): byte counter. Defaults to 0.

    Returns:
        int: amount of bytes to reserve
    """
    if len(tree) == 0:
        return counter

    tree_copy = copy.copy(tree)
    counter_copy = copy.copy(counter)

    head, *tail = tree_copy
    if head.token_type == enums.token_types.VAR:
        counter_copy += 8 # Ik zet de grens op 1 variable op 8 bytes max
    return getAmountOfVarsBytes(tail, counter_copy)

# getNewStackSpotAddress ::dict, str -> int
def getNewStackSpotAddress( variable_memory_adresses : dict, name :str ) -> int:
    """getNewStackSpotAddress supplies the next spot on the reserved stack to store a new variable

    Args:
        variable_memory_adresses (dict): dictionary with current taken addresses.
        name (str): name of var to be stored

    Returns:
        new stackpoint adress relative to R7
    """
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

# startAssemblyCode :: str -> str
def startAssemblyCode(file_name : str) -> str:
    """gives the start code of the assembly code

    Args:
        file_name (str): name of the file

    Returns:
        str: string containing start information assembly
    """
    
    start_txt = ".section .text\n.align 4\n.global " + file_name + "\n"

    return start_txt

# endAssemblyCode :: List[str], List[int] ->
def endAssemblyCode(word_List : List[str], line_numbers : List[int]) -> str:
    """gives the end of assembly code

    Args:
        word_List (List[str]): list of al strings in the code
        line_numbers (List[int]): list of al passed line numbers

    Returns:
        str: [description]
    """
    word_List_copy = copy.copy(word_List)
    end_txt = "\nB end_of_program"
    end_txt += "\n" + createLookupTable(line_numbers)
    end_txt += "\n\nend_of_program:"
    end_txt += "\nMOV SP, R6"
    end_txt += "\nPOP {R4,R5,R6,R7,PC}"

    end_txt += "\n\nend_of_program_error:"
    end_txt += "\nLDR R0, =Standard_Error"
    end_txt += "\nBL print_word"
    end_txt += "\nMOV SP, R6"
    end_txt += "\nPOP {R4,R5,R6,R7,PC}"

    word_List_copy += ["Standard Error"]
    end_txt += addWords(word_List_copy)

    return end_txt

# addWords :: List[str], str
def addWords(word_List : List[str], asm_string : str = "") -> str:
    """addWords creates the data segment with al strings saves as .asciz

    Args:
        word_List (List[str]): list of al strings to be saved
        asm_string (str, optional): string containing data segment. Defaults to "".

    Returns:
        str: data segments
    """
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

# printValueBase :: support.Node, List[str] -> 
def printValueBase( node: support.Node, word_List : List[str] ) -> str:
    """print a base node value

    Args:
        node (support.Node): node whose value is to be printed
        word_List (List[str]): list of al strings in code

    Returns:
        str: print commands
    """
    value, word_List_copy, value_type = compilerBase(node.value, word_List)
    if value_type == enums.token_types.STRING:
        load_into_R0 = "\nLDR R0, " + value
        print_statement = "\nBL print_word"
    else:
        load_into_R0 = "\nMOV R0, " + value
        print_statement = "\nBL print_number"
    return load_into_R0 + print_statement, word_List_copy

# getFoundFuncsOffsetDict :: List[str], str, dict, int -> dict
def getFoundFuncsOffsetDict( found_funcs : List[str], main_fileName : str, new_dict : dict = {}, counter : int = 0 ) -> dict:
    """get offset dictionaty for function line numbers, main code : 0 based, first func 100 + line nr etc.

    Args:
        found_funcs (List[str]): al found functions in code
        main_fileName (str): name of the code file
        new_dict (dict, optional): dictionary that hods offset, name func = key. Defaults to {}.
        counter (int, optional): counter at which offset we are. Defaults to 0.

    Returns:
        dict: dictionary containing function offset
    """
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

# createLookupTable :: List[str], str -> str
def createLookupTable( line_numbers : List[str], asm_string : str = "\nlookUpTable:" ) -> str:
    """creates a lookup table for branching to lien number labels

    Args:
        line_numbers (List[str]): list of al found line numbers
        asm_string (str, optional): asm commands to execute. Defaults to "\nlookUpTable:".

    Returns:
        str: lookup table asm commands
    """
    line_numbers_copy = copy.copy(line_numbers)
    asm_string_copy = copy.copy(asm_string)

    if len(line_numbers_copy) == 0:
        return asm_string_copy+"\nBNE end_of_program_error"

    head, *tail = line_numbers_copy

    asm_string_copy += "\nCMP R0, #" + str(head)
    asm_string_copy += "\nBEQ _line_" + str(head)
    return createLookupTable(tail, asm_string_copy)

# def compile( str,List[list_types], dict,str ,dict, List[str], dict, List[int]): -> Tuple[str, dict, List[str], List[int]]
list_types = TypeVar(support.Node, support.VariableNode, support.MathNode, support.Error)
def compile( main_func_name : str, ast: List[list_types], found_funcs : dict, asm_string : str = "", variable_memory_adresses : dict = {}, word_List : List[str] = [], func_offset : dict = {}, line_numbers : List[int] = []) -> Tuple[str, dict, List[str], List[int]]:
    """main compile function

    Args:
        main_func_name (str): name of current code segment
        ast (List[list_types]): parser tree to compile
        found_funcs (dict): dictionary al functions in code
        asm_string (str, optional): assembly code. Defaults to "".
        variable_memory_adresses (dict, optional): dictionary containing variable memory stack adresses. Defaults to {}.
        word_List (List[str], optional): list of strings that occured in code. Defaults to [].
        func_offset (dict, optional): function offset dictionary. Defaults to {}.
        line_numbers (List[int], optional): list op al passed line numbers. Defaults to [].

    Returns:
        Tuple[str, dict, List[str], List[int]]: assembly code, memory addresses, word list, line numbers list
    """
    if len(ast) == 0:
        return asm_string, variable_memory_adresses, word_List, line_numbers

    ast_copy = copy.copy(ast)
    found_funcs_copy = copy.copy(found_funcs)
    variable_memory_adresses_copy = copy.copy(variable_memory_adresses)
    word_List_copy = copy.copy(word_List)
    line_numbers_copy = copy.copy(line_numbers)

    if asm_string == "":
        amount_of_bytes_to_reserve = getAmountOfVarsBytes(ast_copy)
        func_offset = getFoundFuncsOffsetDict( ["code"]+ list(found_funcs.values()), main_func_name )
        if main_func_name not in found_funcs.keys():
            asm_string_copy, word_List_copy, line_numbers_copy =  compileAlFunctions(list(found_funcs.values()), main_func_name, found_funcs_copy, word_List_copy)    
        else:
            asm_string_copy = copy.copy(asm_string)
        asm_string_copy += "\n\n" + main_func_name + ":"  
        if main_func_name in found_funcs.keys():
            asm_string_copy += "\nPUSH {R7,LR}"
        else:
            asm_string_copy += "\nPUSH {R4,R5,R6,R7,LR}"
            asm_string_copy += "\nMOV R6, SP"
        asm_string_copy += "\nSUB SP, SP, #" + str(amount_of_bytes_to_reserve)        
        asm_string_copy += "\nADD R7, SP, #0"
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


# compilerBase :: support.Node, List[str] -> str
def compilerBase( node: support.Node, word_List : List[str] ) -> str:
    """generate assembly code of base type node

    Args:
        node (support.Node): current node to compile
        word_List (List[str]): list of all past strings

    Returns:
        str: assembly code
    """
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

# compilerVariable :: support.VariableNode, str, dict, dict, List[str] -> Tuple[str, dict, List[int]]
def compilerVariable( node: support.VariableNode, main_func_name : str, variable_memory_adresses : dict, func_offset : dict, word_List : List[str] ) -> Tuple[str, dict, List[int]]:
    """compile a variable

    Args:
        node (support.VariableNode): variableNode
        main_func_name (str): current code block name
        variable_memory_adresses (dict): dictionary containing variable memory stack adresses.
        func_offset (dict): dictionary containing function offset
        word_List (List[str]): List of al passed strings

    Returns:
        Tuple[str, dict, List[int]]: assembly code, variable_memery addres, word_list
    """
    variable_memory_adresses_copy = copy.copy(variable_memory_adresses)
    node_copy = copy.copy(node)
    word_List_copy = copy.copy(word_List)
    main_func_name_copy = copy.copy(main_func_name)

    assembly_string = ""

    if node_copy.token_type == enums.token_types.OUT:
        if node_copy.value.node_type == enums.node_types.VAR:
            load_value = "\nLDR R3,[R7, #" + str(variable_memory_adresses_copy[main_func_name + node.value.variable_name][0]) + "]"
            load_into_R0 = "\nMOV R0, R3"
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
            load_value = "\nLDR R3,[R7,#" + str(variable_memory_adresses_copy[main_func_name +node.value.variable_name][0]) + "]"
            load_into_R0 = "\nMOV R0, R3"
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
                load_into_R0 = "\nLDR R3, " + value
            else:
                load_into_R0 = "\nMOV R3, " + value
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
                load_into_R0 = "\nLDR R3, " + value
            else:
                load_into_R0 = "\nMOV R3, " + value
            store = "\nSTR R3,[R7,#" + adress + "]" 
            assembly_string += load_into_R0 + store
            variable_memory_adresses_copy[main_func_name + node_copy.variable_name] = [int(adress), 8, node_copy.value.token_type]
        elif node_copy.value.node_type == enums.node_types.VAR or node_copy.value.node_type == enums.node_types.INPUT:
            load_var_value = "\nLDR R3,[R7,#" + str(variable_memory_adresses[main_func_name+ node.value.variable_name][0]) + "]"
            new_address = getNewStackSpotAddress(variable_memory_adresses_copy, main_func_name + node_copy.variable_name)
            new_address = str(new_address)
            restore_under_new_var_name = "\nSTR R3,[R7,#" + new_address + "]" 
            assembly_string += load_var_value + restore_under_new_var_name
            base_type = variable_memory_adresses[main_func_name+node.value.variable_name][2]
            variable_memory_adresses_copy[main_func_name +node_copy.variable_name] = [int(new_address), 8, base_type ]

    return assembly_string, variable_memory_adresses_copy, word_List_copy

# compilerMath :: support.MathNode, str, dict, List[str] -> Tuple[str, dict]
def compilerMath( node: support.MathNode, main_func_name : str, variable_memory_adresses : dict, word_List : List[str]) -> Tuple[str, dict]:
    """compile math node

    Args:
        node (support.MathNode): math node to compile
        main_func_name (str): name of current code block
        variable_memory_adresses (dict): dictionary containing variable memory stack adresses.
        word_List (List[str]): List of al past strings

    Returns:
        Tuple[str, dict]: assembly code, variable_memory addresses
    """
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

    return command_start, variable_memory_adresses_copy, word_List_copy

# compilerIf :: support.IfNode, str, dict, List[str], dict -> Tuple[str,dict,List[str]]
def compilerIf( node: support.IfNode, main_func_name : str, variable_memory_adresses : dict, word_List : List[str], func_offset : dict ) -> Tuple[str,dict,List[str]]:
    """compile if node

    Args:
        node (support.IfNode): ifNode to compile
        main_func_name (str): name of current code block
        variable_memory_adresses (dict): dictionary containing variable memory stack adresses.
        word_List (List[str]):List of al past Strings
        func_offset (dict): dictionary of function offset

    Returns:
        Tuple[str,dict,List[str]]: assembly code, variable_memory_addresses, word_list
    """
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

# compilerFunctionCall :: support.FunctionCall, str, dict, dict, List[str] ->Tuple[str,dict,List[str]]
def compilerFunctionCall( node: support.FunctionCall, main_func_name : str, found_funcs : dict, variable_memory_adresses : dict, word_List : List[str])->Tuple[str,dict,List[str]]:
    """compile function call

    Args:
        node (support.FunctionCall): functionCall node to compile
        main_func_name (str): name of current code block
        found_funcs (dict): al functions in code
        variable_memory_adresses (dict): dictionary containing variable memory stack adresses.
        word_List (List[str]): List of al past strings

    Returns:
        Tuple[str,dict,List[str]]: assembly code, variable_memory_addresses, word_list
    """
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
    mov_into_r1 = "\nMOV R1, R0"
    save_var_func_result = "\nSTR R1, [R7,#" + str(new_address) + "]"
    variable_memory_adresses_copy[main_func_name +node_copy.output.variable_name] = [new_address, 8, enums.token_types.INT]
    return give_input+link_to_function+mov_into_r1+save_var_func_result, variable_memory_adresses_copy, word_List_copy

# compileAlFunctions :: List[support.FunctionNode], str, dict, dict, List[str], str, List[int] -> Tuple[str, List[str], List[int]]
def compileAlFunctions( found_func : List[support.FunctionNode], main_func_name : str, found_funcs : dict, word_List : List[str], asm_string: str = "", line_numbers : List[int] = []) -> Tuple[str, List[str], List[int]]:
    """create assembly code all functions

    Args:
        found_func (List[support.FunctionNode]): list of al functions
        main_func_name (str): current code block name
        found_funcs (dict): dict of al found functions
        word_List (List[str]): list of al past strings
        asm_string (str, optional): assembly code. Defaults to "".
        line_numbers (List[int], optional): list of al passed line numbers. Defaults to [].

    Returns:
        Tuple[str, List[str], List[int]]: assembly code, word_list, line_numbers
    """
    found_func_copy = copy.copy(found_func)
    main_func_name_copy = copy.copy(main_func_name)
    word_List_copy = copy.copy(word_List)
    asm_string_copy = copy.copy(asm_string)
    found_funcs_copy = copy.copy(found_funcs)
    line_numbers_copy = copy.copy(line_numbers)

    if len(found_func) == 0:
        return asm_string_copy, word_List_copy, line_numbers_copy

    head, *tail = found_func
   
    add_string, word_List_copy, line_numbers_copy = compilerFunction(head, head.value, found_funcs_copy, word_List_copy, line_numbers_copy)
    asm_string_copy += add_string

    return compileAlFunctions(tail, main_func_name_copy, found_funcs_copy, word_List_copy, asm_string_copy, line_numbers_copy)
 
# compilerFunction :: support.FunctionNode, str, dict, List[str], List[int], str -> Tuple[str, List[str], List[int]]
def compilerFunction( node: support.FunctionNode, main_func_name : str, found_funcs: dict, word_List : List[str], line_numbers : List[int] ,asm_string: str = "") -> Tuple[str, List[str], List[int]]:
    """compile a single function

    Args:
        node (support.FunctionNode): functionNode to compile
        main_func_name (str): name of current code block
        found_funcs (dict): al found functions
        word_List (List[str]): list of al past strings
        line_numbers (List[int]): list of al past line numbers
        asm_string (str, optional): assembly code. Defaults to "".

    Returns:
        Tuple[str, List[str], List[int]]: assembly code, word_list, line_numbers
    """
    node_copy = copy.copy(node)
    main_func_name_copy = copy.copy(main_func_name)
    word_List_copy = copy.copy(word_List)
    found_funcs_copy = copy.copy(found_funcs)
    line_numbers_copy = copy.copy(line_numbers)
    
    amount_of_bytes_to_reserve = getAmountOfVarsBytes(node_copy.commands)
    end_string = "\nMOV SP, R7"
    end_string += "\nADD SP, SP, #" + str(amount_of_bytes_to_reserve)
    end_string += "\nPOP {R7, PC}\n"
    string, variable_memory_adresses_copy, word_List_copy, line_numbers_copy =  compile(node_copy.value, node_copy.commands, found_funcs_copy, word_List=word_List_copy, line_numbers=line_numbers_copy)
    string += end_string

    return string, word_List_copy, line_numbers_copy
    
# compilerFUnctionInput :: support.VariableNode, str, dict, List[str] -> Tuple[str, List[str], List[int]]:
def compilerFunctionInput(node: support.VariableNode, main_func_name : str, variable_memory_adresses : dict, word_List : List[str]) ->Tuple[str, List[str], List[int]]:
    """compile function input node

    Args:
        node (support.VariableNode): function input to compile
        main_func_name (str): name of current code block
        variable_memory_adresses (dict): dictionary containing variable memory stack adresses.
        word_List (List[str]): list of al passed strings

    Returns:
        Tuple[str, List[str], List[int]]:  assembly code, variable_memory_adresses, word_list
    """
    variable_memory_adresses_copy = copy.copy(variable_memory_adresses)
    word_List_copy = copy.copy(word_List)

    new_address = getNewStackSpotAddress( variable_memory_adresses_copy,  main_func_name + node.variable_name)
    store_input_value = "\nSTR R0, [R7,#" + str(new_address) + "]"
    variable_memory_adresses_copy[main_func_name + node.variable_name] = [new_address, 8, enums.token_types.INT]

    return store_input_value, variable_memory_adresses_copy, word_List_copy
    