from typing import List
import operator
import enums
import interpreter

class Node(object):
    def __init__(self, value, node_type):
        self.value = value
        self.node_type = node_type

    def __str__(self):
        return 'Node({value}, {node_type})'.format(
            value=self.value,
            node_type=self.node_type
        )

    def __repr__(self):
        return self.__str__()

class Parser(object):
    def __init__(self, tokens : List[interpreter.Token]=None, types : enums.token_types = None):
        self.tokens = tokens
        self.token_index = 0
        self.state = enums.parser_states.IDLE

    def parse(self, token_list : List[interpreter.Token]= None ):
        if len( token_list ) == 0:
            return

        head, *tail = token_list

        value = head.value
        token_type = head.token_type
        
        if self.state == enums.parser_states.IDLE:
            if token_type == enums.token_types.FROM:
                # found starting FROM statement
                
            

        return
