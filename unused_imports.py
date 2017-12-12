import ast
from collections import defaultdict
# from builtin_functions import builtin_functions

unused_imports = defaultdict()
redefined_imports_assign = defaultdict(list)
redefined_imports_args = defaultdict(list)

class UnusedImports(ast.NodeVisitor):
    
    def __init__(self):
        pass
    
    def visit_Module(self, node):
        for body in node.body:
            if isinstance(body, ast.Import):
                self.getImport(body)
            elif isinstance(body, ast.ImportFrom):
                self.getImportFrom(body)
            else:
                break
    
    def getImport(self, node):
        for alias in node.names:
            if not alias.asname:
                unused_imports[alias.name] = node.lineno
            else:
                unused_imports[alias.asname] = node.lineno
 
                            
    def getImportFrom(self, node):
        for alias in node.names:
            if not alias.asname:
                if alias.name != '*':
                    unused_imports[alias.name] = node.lineno
            else:
                unused_imports[alias.asname] = node.lineno  
                
class UnusedImports2(ast.NodeVisitor):
    
    def __init__(self):
        pass
        
    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                if target.id in unused_imports:
                    redefined_imports_assign[target.id].append(node.lineno)
    
    def visit_FunctionDef(self, node):
        if 'args' in dir(node.args):
            end_line = self.check_last_body(node)
            for args in node.args.args:
                if args.arg in unused_imports:
                    redefined_imports_args[args.arg].append((node.lineno, end_line))
    
    def check_last_body(self, body):
        end_line = body.lineno
        while 'body' in dir(body):
            end_line = body.body[-1].lineno
            body = body.body[-1]
        return end_line        

class UnusedImports3(ast.NodeVisitor):
    
    def __init__(self):
        pass
    
    def check_skip(self, node):
        lineno = node.lineno
        for arg in redefined_imports_assign:
            for key in redefined_imports_assign[arg]:
                if key <= lineno:
                    return True
        for arg in redefined_imports_args:
            for key in redefined_imports_args[arg]:
                if key[0] <= lineno:
                    if key[1] >= lineno:
                        return True
        return False
    
    
    def visit_Assign(self, node): 
        if self.check_skip(node):
            return
        for target in node.targets:
            if isinstance(target, ast.Attribute):
                self.check_import(target)
            if isinstance(target, ast.Subscript):
                _slice = target.slice
                if isinstance(_slice, ast.Index):
                    self.check_import(_slice)
                if isinstance(_slice, ast.Slice):
                    lower = _slice.lower
                    upper = _slice.upper
                    step = _slice.step
                    self.check_import(lower)
                    self.check_import(upper)  
                    self.check_import(step)
        #value check done after check for targets
        if isinstance(node.value, ast.Dict):
            self.check_dict(node.value)
        if isinstance(node.value, ast.Num) or isinstance(node.value, ast.Str):
            return 
        if isinstance(node.value, ast.List) or isinstance(node.value, ast.Tuple):
            self.check_elements(node.value)
        if 'value' in dir(node):                      
            node = node.value
            self.check_import(node)
        
    def visit_Expr(self, node):
        if self.check_skip(node):
            return     
        if 'value' in dir(node):
            self.check_import(node.value)
            
    def visit_Name(self, node):
        if node.id in unused_imports:
            del unused_imports[node.id]
                
    def check_import(self, node):
        while 'id' not in dir(node):
            self.check_args(node)
            if 'func' in dir(node):
                node = node.func
            elif 'value' in dir(node):
                node = node.value
            else:
                break
        if 'id' in dir(node):
            if node.id in unused_imports:
                del unused_imports[node.id]
                
    def check_args(self,node):
        if 'args' in dir(node):
            for arg in node.args:
                self.check_import(arg)        
    
    def check_dict(self, node):
        if 'key' in dir(node):
            for key in node.keys:
                self.general_check(key)
        if 'values' in dir(node):
            for value in node.values:
                self.general_check(value)
                
    def check_elements(self, node):
        if 'elts' in dir(node):
            for elt in node.elts:
                self.general_check(elt)
    
    def general_check(self, node):
        if isinstance(node, ast.Name):
            self.visit_Name(node)
        elif isinstance(node, ast.Dict):
            self.check_dict(node)
        elif isinstance(node, ast.List) or isinstance(node, ast.Tuple):
            self.check_elements(node)
        else:
            if 'value' in dir(node):
                self.check_import(node)
                
                
        
                
                
                