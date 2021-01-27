from typing import List, TypeVar, Union, Tuple
import copy

import lexer
import parser
import enums
import support
import compiler_base

def main():
    file_name = input("enter file name without extension: ")
    # file_name = "test_subroutines_1"
    lexed = lexer.lexen(file_name+".txt")
    parse = parser.Parser()
    tree, found_funcs = parse.parse(lexed)

    if len(tree) == 1 and type(tree[0]) == support.Error:
        print(tree[0])
    else:
        compiled_txt,mem_,word_list,line_numbers = compiler_base.compile( file_name, tree, found_funcs)
        compiled_txt = compiler_base.startAssemblyCode( file_name, list(found_funcs.keys())) + compiled_txt
        compiled_txt += compiler_base.endAssemblyCode(word_list, line_numbers)

        output_path = "/home/cunera/Documents/hu-environment/modules/ATP/code/"
        output_file_name = file_name + ".asm"
        f = open(output_path + output_file_name, "w")
        f.write(compiled_txt)
        f.close()
        
        print(compiled_txt)



main()