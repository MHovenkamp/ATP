from typing import List, TypeVar, Union, Tuple
import copy

import lexer
import parser
import enums
import support
import compiler_base

def main():
    file_name = "code"
    lexed = lexer.lexen(file_name+".txt")
    parse = parser.Parser()
    tree, found_funcs = parse.parse(lexed)

    # for item in tree:
    #     print(item)
    compiled_txt,mem_,word_list = compiler_base.compile( file_name, tree, found_funcs)
    compiled_txt += compiler_base.endAssemblyCode(word_list)

    output_path = "/home/cunera/Documents/hu-environment/modules/ATP/code/"
    output_file_name = file_name + ".asm"
    f = open(output_path + output_file_name, "w")
    f.write(compiled_txt)
    f.close()
    
    print(compiled_txt)



main()