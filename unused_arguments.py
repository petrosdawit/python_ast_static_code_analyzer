import ast
from collections import defaultdict
# from builtin_functions import builtin_functions

unused_arguments = defaultdict()
functions = defaultdict()
can_have_self = set()

class UnusedArguments(ast.NodeVisitor):
    
    def __init__(self):
        pass
    
    def visit_Module(self, node):
        for body in node.body:
            if isinstance(body, ast.ClassDef):
                body = body.body
                for b in body:
                    if isinstance(b, ast.FunctionDef):
                        can_have_self.add(b.name)
                        
                
        
        
class UnusedArguments2(ast.NodeVisitor):
    
    def __init__(self):
        pass
    
    def visit_FunctionDef(self, node):
        function_name = node.name
        function_lineno = node.lineno
        current_unused_args = defaultdict(list)
        functions[function_name] = node.lineno
        for arg in node.args.args:
            if arg.arg == 'self' and function_name in can_have_self:
                continue
            current_unused_args[function_name, function_lineno].append(arg.arg)
        
        def helper_value(node):
            if 'args' in dir(node):
                for arg in node.args:
                    if isinstance(arg, ast.Call):
                        helper_value(arg)
                    if 'id' in dir(arg):
                        arguments_check(arg)
        
        def arguments_check(node):
            if 'id' in dir(node):
                arguments = current_unused_args[function_name, function_lineno]
                for c_arg in arguments:
                    if c_arg == node.id:
                        arguments.remove(c_arg)
                current_unused_args[function_name, function_lineno] = arguments  
    
        def arguments_upper_layer_check(node):
            if 'args' in dir(node):
                for arg in node.args:
                    arguments_upper_layer_check(arg)
            while 'id' not in dir(node):
                if 'func' in dir(node):
                    node = node.func
                elif 'value' in dir(node):
                    node = node.value
                else:
                    break
            arguments_check(node)
                                  
        def body_check(body): 
            #what to check for:
            #return, assign, call, if, while, for, subscript
            #done: call/value, for
            if 'value' in dir(body):
                helper_value(body.value)
            if isinstance(body, ast.For):
                if isinstance(body.iter, ast.Name):
                    arguments_upper_layer_check(body.iter)           
                else:
                    if isinstance(body.iter, ast.Call):
                        helper_value(body.iter)
                for b in body.body:
                    body_check(b)
            if isinstance(body, ast.With):
                for item in body.items:
                    body_check(item)
            if isinstance(body, ast.withitem):
                body_check(body.context_expr)
                body_check(body.optional_vars)
            if isinstance(body, ast.While) or isinstance(body, ast.If):     
                #special
                test = body.test
                if isinstance(test, ast.Compare):
                    if isinstance(test.left, ast.Name):
                        arguments_upper_layer_check(test.left)
                    for c in test.comparators:
                        arguments_upper_layer_check(c)
                if isinstance(test, ast.BoolOp):
                    for value in test.values:
                        body_check(value)
                if isinstance(test, ast.Name):
                    arguments_upper_layer_check(test)
                for b in body.body:
                    body_check(b)
            if isinstance(body, ast.Return):
                value = body.value
                if isinstance(value, ast.BinOp):
                    body_check(value.left)
                    body_check(value.right)
                else:
                    arguments_upper_layer_check(value)
            if isinstance(body, ast.BinOp):
                if not isinstance(body.left, ast.BinOp):
                    arguments_upper_layer_check(body.left)
                else:
                    body_check(body.left)
                if not isinstance(body.right, ast.BinOp):
                    arguments_upper_layer_check(body.right)
                else:
                    body_check(body.right)
            if isinstance(body, ast.Compare):
                if isinstance(body.left, ast.Name):
                    arguments_upper_layer_check(body.left)
                for c in body.comparators:
                    arguments_upper_layer_check(c)
            if isinstance(body, ast.BoolOp):
                for value in body.values:
                    body_check(value)
            if isinstance(body, ast.Name):
                arguments_upper_layer_check(body)
            if 'value' in dir(body):
                body_check(body.value)
            if 'targets' in dir(body):
                for target in body.targets:
                    body_check(target) 
            if isinstance(body, ast.Name):
                arguments_upper_layer_check(body)
            if isinstance(body, ast.Subscript):
                value = body.value
                arguments_upper_layer_check(value)
                _slice = body.slice
                if isinstance(_slice, ast.Index):
                    arguments_upper_layer_check(_slice)
                if isinstance(_slice, ast.Slice):
                    lower = _slice.lower
                    upper = _slice.upper
                    arguments_upper_layer_check(lower)
                    arguments_upper_layer_check(upper)  
            if isinstance(body, ast.Call):
                helper_value(body) 
            if isinstance(body, ast.If):
                body_check(body.test)
                for b in body.body:
                    body_check(b)
            if isinstance(body, ast.For):
                body_check(body.target)
                body_check(body.iter)
                for b in body.body:
                    body_check(b)
                
                        
        for body in node.body:        
            body_check(body)
        unused_arguments.update(current_unused_args)
        
        

                