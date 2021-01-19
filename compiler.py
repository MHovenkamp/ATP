from typing import List, TypeVar, Union, Tuple
import copy

import lexer
import parser
import enums
import support
import compiler_base

list_types = TypeVar(support.Node, support.VariableNode, support.MathNode, support.Error)
def compile( file_name : str, ast: List[list_types], found_funcs : dict, asm_string : str = "", variable_memory_adresses : dict = {}, word_List : List[str] = []):

    if len(ast) == 0:
        asm_string += compiler_base.endAssemblyCode(word_List)
        return asm_string

    ast_copy = copy.copy(ast)
    found_funcs_copy = copy.copy(ast)
    variable_memory_adresses_copy = copy.copy(variable_memory_adresses)
    word_List_copy = copy.copy(word_List)

    if asm_string == "":
        asm_string_copy = compiler_base.startAssemblyCode( ast_copy, file_name)
    else:
        asm_string_copy = copy.copy(asm_string)

    head, *tail = ast_copy

    asm_string_copy += "\nline_" + str(head.line_nr) + ":"

    if head.node_type == enums.node_types.VAR:
        string, variable_memory_adresses_copy, word_List_copy = compiler_base.compilerVariable(head, variable_memory_adresses_copy, word_List_copy)
        asm_string_copy += string
    
    elif head.node_type == enums.node_types.MATH:
        string, variable_memory_adresses_copy, word_List_copy = compiler_base.compilerMath(head, variable_memory_adresses_copy, word_List_copy)
        asm_string_copy += string

    return compile( file_name, tail, found_funcs_copy, asm_string_copy, variable_memory_adresses_copy, word_List_copy)


def main():
    file_name = "code"
    lexed = lexer.lexen(file_name+".txt")
    parse = parser.Parser()
    tree, found_funcs = parse.parse(lexed)

    # for item in tree:
    #     print(item)

    compiled_txt = compile( file_name, tree, found_funcs)
    
    output_path = "/home/cunera/Documents/hu-environment/modules/ATP/code/"
    output_file_name = file_name + ".asm"
    f = open(output_path + output_file_name, "w")
    f.write(compiled_txt)
    f.close()
    
    print(compiled_txt)



main()