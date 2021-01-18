from typing import List, TypeVar, Union, Tuple
import copy

import lexer
import parser
import enums
import support
import compiler_base

list_types = TypeVar(support.Node, support.VariableNode, support.MathNode, support.Error)
def compile( file_name : str, ast: List[list_types], found_funcs : dict, asm_string : str = "", variable_memory_adresses : dict = {}, available_registers: dict = {"empty":0}):

    if len(ast) == 0:
        return asm_string

    ast_copy = copy.copy(ast)
    found_funcs_copy = copy.copy(ast)
    variable_memory_adresses_copy = copy.copy(variable_memory_adresses)

    if asm_string == "":
        asm_string_copy = compiler_base.start_assembly_code( ast_copy, file_name)
    else:
        asm_string_copy = copy.copy(asm_string)

    head, *tail = ast_copy

    asm_string_copy += "\nline_" + str(head.line_nr) + ":"

    if head.node_type == enums.node_types.VAR:
        string, variable_memory_adresses_copy = compiler_base.compilerVariable(head, variable_memory_adresses_copy)
        asm_string_copy += string
    
    elif head.node_type == enums.node_types.MATH:
        string, variable_memory_adresses_copy = compiler_base.compilerMath(head, variable_memory_adresses_copy)
        asm_string_copy += string

    return compile( file_name, tail, found_funcs_copy, asm_string_copy, variable_memory_adresses_copy)


def main():
    lexed = lexer.lexen("code.txt")
    parse = parser.Parser()
    tree, found_funcs = parse.parse(lexed)
    print(tree)
    compiled_txt = compile( "test", tree, found_funcs)
    print(compiled_txt)



main()