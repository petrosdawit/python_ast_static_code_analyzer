import ast
from collections import defaultdict
from builtin_functions import builtin_functions

unreachable_lines = defaultdict(list)
advisedNotUsedBuiltins = set()
class_protected_members = defaultdict(set)
using_args_kwargs = defaultdict()
specific_exceptions = defaultdict()
exception_does_nothing = defaultdict()
dangerous_defaults = set()
unnecessary_forelse = set()
unnecessary_whileelse = set()
misplaced_imports = set()

class UnreachableCode(ast.NodeVisitor):
    
    def __init__(self):
        pass

    def visit_FunctionDef(self, node):
        unreachable_code = []
        end_line = node.body[-1].lineno
        key = (node.name, node.lineno)
        accepted_true = defaultdict(list)
        accepted_false = defaultdict(list)
        
        def get_accepted(node):
            for body in node.body:
                if isinstance(body, ast.Assign):
                    for target in body.targets:
                        if 'id' in dir(target):
                            if isinstance(body.value, ast.Num):
                                if body.value.n:
                                    accepted_true[body.targets[0].id].append(body.lineno)
                                else:
                                    accepted_false[body.targets[0].id].append(body.lineno)
                            if isinstance(body.value, ast.NameConstant):
                                if body.value.value:
                                    accepted_true[body.targets[0].id].append(body.lineno)
                                else:
                                    accepted_false[body.targets[0].id].append(body.lineno)  
            return accepted_true, accepted_false                      
                        
        get_accepted(node)
        
        def handle_true(node):
            test = node.test
            body = node.body
            start_line = node.lineno
            evaluated_bool = False
            if isinstance(test, ast.BoolOp) or isinstance(test, ast.UnaryOp) or isinstance(test, ast.Name):
                evaluated_bool = true_check(test, start_line)
            if (isinstance(test, ast.NameConstant) and test.value) or (isinstance(test, ast.Num) and test.n != 0):
                evaluated_bool = True                       
            if evaluated_bool:
                end_expr_line = body[-1].lineno
                if node.orelse:
                    end_expr_line = node.orelse[-1].lineno
                for b in body:
                    if isinstance(b, ast.For):
                        for x in b.body:
                            handle_true(x)
                            handle_false(x)
                    if isinstance(b, ast.If) or isinstance(b, ast.While):
                        handle_true(b)
                        handle_false(b)
                    if b.lineno == end_expr_line:
                        continue
                    if isinstance(b, ast.Return) or isinstance(b, ast.Raise):
                        unreachable_code.append((b.lineno+1, end_line))
                        break
                    if isinstance(b, ast.Continue) or isinstance(b, ast.Break):
                        unreachable_code.append((b.lineno+1, end_expr_line))

        def true_check(test, start_line):
            if (isinstance(test, ast.Name) and test.id in accepted_true):
                t_line, f_line = -1, -1
                for lineno in accepted_true[test.id]:
                    if lineno < start_line:
                        t_line = lineno
                if t_line != -1 and test.id not in accepted_false:
                    return True
                if t_line == -1:
                    return False
                for lineno in accepted_false[test.id]:
                    if lineno < start_line:
                        f_line = lineno
                if f_line == -1:
                    return True
                if f_line > t_line:
                    return True
                return False    
            if (isinstance(test, ast.Name)):
                return False
            op = test.op
            if isinstance(op, ast.Not):
                return False
            values = test.values
            if isinstance(op, ast.And):
                output = True
                for value in values:
                    if isinstance(value, ast.BoolOp) or isinstance(value, ast.UnaryOp) or isinstance(value, ast.Name):
                        if not true_check(value, start_line):
                            return False
                        continue
                    if  (isinstance(value, ast.NameConstant) and value.value) or (isinstance(value, ast.Num) and value.n != 0):
                        continue
                    else:
                        output = False
                        break
                return output
            if isinstance(op, ast.Or):
                output = False
                for value in values:
                    if isinstance(value, ast.BoolOp) or isinstance(value, ast.UnaryOp) or isinstance(value, ast.Name):
                        if true_check(value, start_line):
                            return True
                        continue
                    if (isinstance(value, ast.NameConstant) and value.value) or (isinstance(value, ast.Num) and value.n != 0):
                        output = True
                        break
                return output    
            return False  
                                      
        
        def handle_false(node):
            test = node.test
            body = node.body
            start_line = node.lineno
            evaluated_bool = True
            if isinstance(test, ast.BoolOp) or isinstance(test, ast.UnaryOp) or isinstance(test, ast.Name):
                evaluated_bool = false_check(test, start_line)
            if (isinstance(test, ast.NameConstant) and not test.value) or (isinstance(test, ast.Num) and test.n == 0):
                evaluated_bool = False
            if not evaluated_bool:
                end_expr_line = None
                for b in body:
                    end_expr_line = b.lineno
                unreachable_code.append((node.lineno+1, end_expr_line))
                if node.orelse:
                    end_expr_line = node.orelse[-1].lineno
                    for b in node.orelse:
                        if isinstance(b, ast.For):
                            for x in b.body:
                                handle_true(x)
                                handle_false(x)
                        if isinstance(b, ast.If) or isinstance(b, ast.While):
                            handle_true(b)
                            handle_false(b)
                        if b.lineno == end_expr_line:
                            continue
                        if isinstance(b, ast.Return) or isinstance(b, ast.Raise):
                            unreachable_code.append((b.lineno+1, end_line))
                            break
                        if isinstance(b, ast.Continue) or isinstance(b, ast.Break):
                            unreachable_code.append((b.lineno+1, end_expr_line))
        
        def false_check(test, start_line):
            if (isinstance(test, ast.Name) and test.id in accepted_false):
                t_line, f_line = -1, -1
                for lineno in accepted_false[test.id]:
                    if lineno < start_line:
                        f_line = lineno
                if f_line != -1 and test.id not in accepted_true:
                    return False
                if f_line == -1:
                    return True
                for lineno in accepted_true[test.id]:
                    if lineno < start_line:
                        t_line = lineno
                if t_line == -1:
                    return False
                if f_line > t_line:
                    return False
                return True 
            if (isinstance(test, ast.Name)):
                return True                     
            op = test.op
            if isinstance(op, ast.Not):
                return True
            values = test.values
            if isinstance(op, ast.And):
                output = True
                for value in values:
                    if isinstance(value, ast.BoolOp) or isinstance(value, ast.UnaryOp) or isinstance(value, ast.Name):
                        if not false_check(value, start_line):
                            return False
                        continue
                    if  (isinstance(value, ast.NameConstant) and not value.value) or (isinstance(value, ast.Num) and value.n == 0):
                        output = False
                        break
                    else:
                        continue
                return output
            if isinstance(op, ast.Or):
                output = False
                for value in values:
                    if isinstance(value, ast.BoolOp) or isinstance(value, ast.UnaryOp) or isinstance(value, ast.Name):
                        if false_check(value, start_line):
                            return True
                        continue
                    if (isinstance(value, ast.NameConstant) and not value.value) or (isinstance(value, ast.Num) and value.n == 0):
                        continue
                    else:
                        output = True
                        break
                return output    
            return True
        
        def merge(unreachable_lines):
            if not unreachable_lines:
                return None
            current_start = unreachable_lines[0][0]
            current_end = unreachable_lines[0][1]
            output = []
            for arr in unreachable_lines:
                if arr[0] > current_end:
                    output.append((current_start,current_end))
                    current_start = arr[0]
                    current_end = arr[1]
                else:
                    current_end = max(current_end, arr[1])
            output.append((current_start, current_end))
            return output

        for body in node.body:
            if isinstance(body, ast.For):
                for b in body.body:
                    if 'test' and 'body' in dir(b):
                        handle_true(b)
                        handle_false(b)
            if isinstance(body, ast.If) or isinstance(body, ast.While):
                handle_true(body)
                handle_false(body)
            if body.lineno == end_line:
                continue
            if isinstance(body, ast.Return) or isinstance(body, ast.Raise):
                unreachable_code.append((body.lineno+1, end_line))

        
        unreachable_code = merge(unreachable_code)
        if unreachable_code:
            unreachable_lines[key].append(unreachable_code)
                    
    
class AdvisedNotUsedBuiltins(ast.NodeVisitor):
    
    def __init__(self):
        self.advisedNotUsedBuiltins = set(['exec'])
    
    def visit_Call(self, node):
        f = node.func
        if isinstance(f, ast.Name):
            if f.id in self.advisedNotUsedBuiltins:
                advisedNotUsedBuiltins.add((f.id, node.lineno))
    
class ArgKeyArgsCheck(ast.NodeVisitor):
    
    def __init__(self):
        pass
    
    def visit_FunctionDef(self, node):
        if node.args.vararg or node.args.kwarg:
            using_args_kwargs[node.name] = node.lineno
            
class SpecificExceptions(ast.NodeVisitor):
    
    def __init__(self):
        pass
    
    def visit_ExceptHandler(self, node):
        if not node.type:
            specific_exceptions[node] = node.lineno
        safe = False
        for body in node.body:
            if isinstance(body, ast.Raise):
                safe = True
        if not safe:
            exception_does_nothing[node] = node.lineno
        
class DangerousDefaults(ast.NodeVisitor):
    
    def __init__(self):
        pass
    
    def visit_FunctionDef(self, node):
        args = node.args
        if 'defaults' in dir(args):
            for i, default in enumerate(args.defaults, 0):
                if isinstance(default, ast.Dict):
                    dangerous_defaults.add((node.name, args.args[i].arg, 'Dict', node.lineno))
                if isinstance(default, ast.List):
                    dangerous_defaults.add((node.name, args.args[i].arg, 'List', node.lineno))
        
            
            
            
class UnnecessaryForWhileElseLoop(ast.NodeVisitor):
    
    def __init__(self):
        pass
    
    def visit_For(self, node):
        if node.orelse:
            for body in node.body:
                if isinstance(body, ast.Break) or isinstance(body, ast.Return) or isinstance(body, ast.Raise):
                    unnecessary_forelse.add((node.orelse[0].lineno-1, node.lineno))
                if isinstance(body, ast.If):
                    for b in body.body:
                        if isinstance(b, ast.Break) or isinstance(b, ast.Return) or isinstance(b, ast.Raise):
                            unnecessary_forelse.add((node.orelse[0].lineno-1, node.lineno))
                if isinstance(body, ast.For):
                    self.visit_For(body)
                if isinstance(body, ast.While):
                    self.visit_While(body)
                    
    def visit_While(self, node):
        if node.orelse:
            for body in node.body:
                if isinstance(body, ast.Break) or isinstance(body, ast.Return) or isinstance(body, ast.Raise):
                    unnecessary_whileelse.add((node.orelse[0].lineno-1, node.lineno))
                if isinstance(body, ast.If):
                    for b in body.body:
                        if isinstance(b, ast.Break) or isinstance(b, ast.Return) or isinstance(b, ast.Raise):
                            unnecessary_whileelse.add((node.orelse[0].lineno-1, node.lineno))
                if isinstance(body, ast.For):
                    self.visit_For(body)
                if isinstance(body, ast.While):
                    self.visit_While(body)
        
class MisplacedImports(ast.NodeVisitor):
    
    def __init__(self):
        self.ImportCheck = True
        
    
    def visit_Module(self, node):
        for body in node.body:
            if isinstance(body, ast.Import) or isinstance(body, ast.ImportFrom):
                if not self.ImportCheck:
                    misplaced_imports.add(body.lineno)
            else:
                self.ImportCheck = False
                    
    

        
            
            
            
            
            
            
            
            