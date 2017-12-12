import ast
from collections import defaultdict
from builtin_functions import builtin_functions

functions = set()
redefined_functions = defaultdict()

class RedefinedFunctions(ast.NodeVisitor):
    
    def __init__(self):
        pass
    
    def visit_Module(self, node):
        for body in node.body:
            self.recurFunctionCheck(body,' ')
        
    def recurFunctionCheck(self, node, attribute):
        if isinstance(node, ast.FunctionDef):
            function_name = attribute + '.' + node.name
            args = 0
            if 'args' in dir(node):
                args = len(node.args.args)
            if (function_name, args) in functions:
                redefined_functions[(function_name, args)] = node.lineno
            else:
                functions.add((function_name,args))   
            for body in node.body:
                self.recurFunctionCheck(body, function_name)
        if isinstance(node, ast.ClassDef):
            function_name = attribute + '.' + node.name
            for body in node.body:
                if isinstance(body, ast.FunctionDef):
                    #args as well
                    self.recurFunctionCheck(body, function_name)                     
     