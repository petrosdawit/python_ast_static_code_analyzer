import ast
from collections import defaultdict
from builtin_functions import builtin_functions

unused_names = defaultdict(set)
used_names = set()


class UnusedVariable(ast.NodeVisitor):
    
    def __init__(self):
        pass
    
    def visit_Assign(self, node):
        if not node:
            pass
        for target in node.targets:
            if 'id' in dir(target):
                if target.id not in builtin_functions:
                    if target.id not in used_names:
                        if isinstance(target.ctx, ast.Store):
                            unused_names[target.id].add(target.lineno)
                        else:
                            used_names.add(target.id)
                            if target.id in unused_names:
                                del unused_names[target.id]                     
            
    def visit_While(self, node):
        if not node:
            pass
        if node.body:
            for body in node.body:
                if isinstance(body, ast.For):
                    self.visit_For(body)
                if isinstance(body, ast.If):
                    self.visit_If(body)
                if isinstance(body, ast.While):
                    self.visit_While(body)
                if isinstance(body, ast.Assign):
                    self.visit_Assign(body)
    
    def visit_If(self, node):
        if not node:
            pass
        if node.body:
            for body in node.body:
                if isinstance(body, ast.For):
                    self.visit_For(body)
                if isinstance(body, ast.If):
                    self.visit_If(body)
                if isinstance(body, ast.While):
                    self.visit_While(body)
                if isinstance(body, ast.Assign):
                    self.visit_Assign(body)
                    
    def visit_For(self, node):
        if not node:
            pass
        if node.target:
            if isinstance(node.target, ast.Tuple):
                for elt in node.target.elts:
                    unused_names[elt.id].add(node.lineno)
                    # if elt.id in unused_names:
                    #     del unused_names[elt.id]
            else:
                unused_names[node.target.id].add(node.lineno)
                # if node.target.id in unused_names:
                #     del unused_names[node.target.id]
        if node.body:
            for body in node.body:
                if isinstance(body, ast.For):
                    self.visit_For(body)
                if isinstance(body, ast.If):
                    self.visit_If(body)
                if isinstance(body, ast.While):
                    self.visit_While(body)
                if isinstance(body, ast.Assign):
                    self.visit_Assign(body)
                    
    def visit_With(self, node):
        for item in node.items:
            if isinstance(item, ast.withitem):
                context_expr = item.context_expr
                optional_vars = None
                if 'optional_vars' in dir(item):
                    optional_vars = item.optional_vars
                    if isinstance(optional_vars, ast.Name):
                        if optional_vars.id not in builtin_functions:
                            if optional_vars.id not in used_names:
                                if isinstance(optional_vars.ctx, ast.Store):
                                    unused_names[optional_vars.id].add(optional_vars.lineno)
                                else:
                                    used_names.add(optional_vars.id)
                                    if optional_vars.id in unused_names:
                                        del unused_names[optional_vars.id]     
                if isinstance(context_expr, ast.For):
                    self.visit_For(context_expr)
                if isinstance(context_expr, ast.If):
                    self.visit_If(context_expr)
                if isinstance(context_expr, ast.While):
                    self.visit_While(context_expr)
                if isinstance(context_expr, ast.Assign):
                    self.visit_Assign(context_expr)       
                if isinstance(context_expr, ast.Call):
                    self.visit_Call(context_expr)             
        
    def visit_Call(self, node):
        if 'args' in dir(node):
            for arg in node.args:
                self.visit_Call(arg)
        while 'id' not in dir(node):
            if 'func' in dir(node):
                node = node.func
            elif 'value' in dir(node):
                node = node.value
            else:
                break
        if 'id' in dir(node):
            if node.id not in builtin_functions:
                if node.id not in used_names:
                    if isinstance(node.ctx, ast.Store):
                        unused_names[node.id].add(node.lineno)
                    else:
                        used_names.add(node.id)
                        if node.id in unused_names:
                            del unused_names[node.id]     
            
class UnusedVariable2(ast.NodeVisitor):
    
    def __init__(self):
        pass    
    
    def visit_Name(self, node):
        if 'id' in dir(node):
            if node.id not in builtin_functions:
                if isinstance(node.ctx, ast.Store) and node.id not in used_names:
                    unused_names[node.id].add(node.lineno)
                else:
                    if node.id in unused_names:
                        used_names.add(node.id)
                        del unused_names[node.id]    
            
    