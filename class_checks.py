import ast
from collections import defaultdict
from builtin_functions import builtin_functions

constructor_check = defaultdict()
no_self_argument = defaultdict()
outside_attributes = defaultdict()
class_funcs = defaultdict()
static_method_selfs = defaultdict()
redefined_new_class_attributes = defaultdict(set)
all_protected_members = defaultdict()
all_classes = defaultdict(set)
all_class_variables = defaultdict()
using_protected_members = set()

class ConstructorCheck(ast.NodeVisitor):
    
    def __init__(self):
        pass
    
    def visit_ClassDef(self, node):
        constructor_check[node.name] = node.lineno
        for body in node.body:
            if isinstance(body, ast.FunctionDef):
                class_funcs[body] = (body.name, body.lineno)
                first_arg = None
                if body.args.args:
                    if isinstance(body.args.args[0], ast.arg):
                        first_arg = body.args.args[0].arg
                if not first_arg:
                    no_self_argument[(body.name, node.name, body.lineno)] = body.lineno 
                else:
                    first_arg = first_arg.split()
                    if first_arg[0] != 'self' and first_arg[0] != 'cls':
                        no_self_argument[(body.name, node.name, body.lineno)] = body.lineno 
            else:
               if isinstance(body, ast.Assign):
                   for target in body.targets:
                       if isinstance(target, ast.Name):
                           outside_attributes[(target.id, node.name, body.lineno)] = body.lineno
                       if isinstance(target, ast.Attribute):
                          attribute = target.attr
                          if isinstance(target.value, ast.Name):
                              attribute = target.value.id + '.' + attribute
                          while isinstance(target.value, ast.Attribute) or isinstance(target.value, ast.Call):
                              if isinstance(target.value, ast.Attribute):
                                  target = target.value
                                  attribute = target.attr + '.' + attribute
                              else:
                                  target = target.value
                                  attribute = target.func.attr + '()' + '.' + attribute
                                  target = target.func
                          attribute = target.value.id + '.' + attribute
                          outside_attributes[(attribute, node.name, body.lineno)] = body.lineno
                
                        
class ConstructorCheck2(ast.NodeVisitor):
    
    def __init__(self):
        pass
    
    def visit_ClassDef(self, node):
        for body in node.body:
            if isinstance(body, ast.FunctionDef):
                if body.name == '__init__':
                    if node.name in constructor_check:
                        del constructor_check[node.name]   
                    
class StaticMethodsCheck(ast.NodeVisitor):
    
    def __init__(self):
        pass

    def visit_FunctionDef(self, node):
        if node not in class_funcs:
            first_arg = None
            if node.args.args:
                if isinstance(node.args.args[0], ast.arg):
                    first_arg = node.args.args[0].arg
            if first_arg == 'self' or first_arg == 'cls':
                static_method_selfs[node.lineno] = (node.name, first_arg)           
        
class RedefiningName(ast.NodeVisitor):
    
    def __init__(self):
        pass
    
    def visit_ClassDef(self, node):
        self_attributes = findSelfAttributes(node)
        name = node.name
        args = get_args_class(node)
        for body in node.body:
            if isinstance(body, ast.FunctionDef):
                if body.name != '__init__' and 'args' in dir(body):
                    if 'args' in dir(body.args):
                        if body.args.args:
                            if body.args.args[0].arg == 'self' or body.args.args[0].arg == 'cls':
                                for b in body.body:
                                    if isinstance(b, ast.Assign):
                                        self.check_assign(b, body, node, name, args)
    
    def check_assign(self, b, body, node, name, args):
        for target in b.targets:
            if 'attr' in dir(target):
                if 'value' in dir(target): 
                    if isinstance(target.value, ast.Name) and target.value.id == body.args.args[0].arg:
                        key = (name, args, node.lineno)
                        if key in self_attributes:
                            class_attributes = self_attributes[key]
                            if target.attr not in class_attributes:
                                redefined_new_class_attributes[(name, node.lineno)].add((target.attr, target.lineno))
                                                                                

class ClassProtectedMembers(ast.NodeVisitor):
    
    def __init__(self):
        pass
    
    def visit_ClassDef(self, node):  
        args = get_args_class(node)

        all_classes[(node.name, args)].add(node.lineno)   
        self_attributes = findSelfAttributes(node)
        protected_members = defaultdict(set)
        for key, value in self_attributes.items():
            for v in value:
                if len(v) > 2:
                    if v[0] and v[1] == '_':
                        protected_members[key].add(v)  
        for key, value in protected_members.items():
            all_protected_members[key] = value      
            
class ClassProtectedMembers2(ast.NodeVisitor):
    
    def __init__(self):
        pass
        
    def visit_Assign(self, node):
        name = []
        for target in node.targets:
            while not isinstance(target, ast.Name):
                if not isinstance(target, ast.Attribute):
                    return
                name = name + [target.attr]
                target = target.value
        name = '.'.join(name)
        value = node.value
        if isinstance(value, ast.Call):
            func = value.func
            if isinstance(func, ast.Name):
                func = func.id
                args = 0
                for arg in value.args:
                    args += 1
                key = (func, args)
                if key in all_classes:
                    all_class_variables[name] = key
    
class ClassProtectedMembers3(ast.NodeVisitor):
    
    def __init__(self):
        pass
    
    def visit_Attribute(self, node): 
        attr = node.attr 
        classes = set()
        for key, value in all_protected_members.items():
            for v in value:
                if attr == v:
                    classes.add((key[0], key[1]))
        var = node.value
        if isinstance(var, ast.Name):
            var = var.id
        else:
            return 
        if len(attr) > 2 and attr[0] and attr[1] == '_' and (var != 'self' and var != 'cls'):
            for key, value in all_protected_members.items():
                using_protected_members.add((attr, var, node.lineno))   
            
def get_args_class(node):
    args = 0
    for body in node.body:
        if isinstance(body,  ast.FunctionDef):
            if body.name == '__init__':
                if 'args' in dir(body.args):
                    for i in range(1, len(body.args.args)):
                        args += 1
    return args
        
def findSelfAttributes(node):
    output = defaultdict(set)
    name = node.name
    args = get_args_class(node)
    for body in node.body:
        if isinstance(body, ast.FunctionDef):
            if body.name == '__init__' and 'args' in dir(body):
                if 'args' in dir(body.args):
                    if body.args.args:
                        if body.args.args[0].arg == 'self' or body.args.args[0].arg == 'cls':
                            for b in body.body:
                                if isinstance(b, ast.Assign):
                                    output = check_assign(b, body, node, output, name, args)
    return output

def check_assign(b, body, node, output, name, args):
    for target in b.targets:
        if 'attr' in dir(target):
            if 'value' in dir(target): 
                if isinstance(target.value, ast.Name) and target.value.id == body.args.args[0].arg:
                    output[(name, args, node.lineno)].add(target.attr)                                                   
    return output                                        
                                                     