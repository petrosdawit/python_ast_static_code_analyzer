import ast
from collections import defaultdict
from builtin_functions import builtin_functions

shadow_builtins = defaultdict(set)

class ShadowBuiltins(ast.NodeVisitor):
    
    def __init__(self):
        pass
    
    def visit_Assign(self, node):
        for target in node.targets:
            if 'id' in dir(target):
                if target.id in builtin_functions:
                    shadow_builtins[target.lineno].add(target.id)
                    