import ast
import sys
from collections import defaultdict
from builtin_functions import builtin_functions
import unused_variable
import shadow_builtins
import unused_imports
import unused_arguments
import redefined_functions
import class_checks
import specific_checks

if __name__ == '__main__':
    args = sys.argv
    if len(args) < 2:
        print('User Inputs require the path to python file')
    else:
        print()
        filename = args[1]
        warnings = defaultdict(set)
        with open(filename, encoding='utf-8') as f:
            code = f.read()
            tree = ast.parse(code)
            unused_variable.UnusedVariable().visit(tree)
            unused_variable.UnusedVariable2().visit(tree)
            shadow_builtins.ShadowBuiltins().visit(tree)
            unused_imports.UnusedImports().visit(tree)
            unused_imports.UnusedImports2().visit(tree)
            unused_imports.UnusedImports3().visit(tree)
            unused_arguments.UnusedArguments().visit(tree)
            unused_arguments.UnusedArguments2().visit(tree)
            redefined_functions.RedefinedFunctions().visit(tree)
            class_checks.ConstructorCheck().visit(tree)
            class_checks.ConstructorCheck2().visit(tree)
            class_checks.StaticMethodsCheck().visit(tree)
            class_checks.RedefiningName().visit(tree)
            class_checks.ClassProtectedMembers().visit(tree)
            class_checks.ClassProtectedMembers2().visit(tree)
            class_checks.ClassProtectedMembers3().visit(tree)
            specific_checks.UnreachableCode().visit(tree)
            specific_checks.AdvisedNotUsedBuiltins().visit(tree)
            specific_checks.ArgKeyArgsCheck().visit(tree)
            specific_checks.SpecificExceptions().visit(tree)
            specific_checks.MisplacedImports().visit(tree)
            specific_checks.DangerousDefaults().visit(tree)
            specific_checks.UnnecessaryForWhileElseLoop().visit(tree)
            for key in specific_checks.unnecessary_forelse:
                warnings[key[0]].add('Warning: Unnecessary else clause at lineno %s in for loop at lineno %s' % key)
            for key in specific_checks.unnecessary_whileelse:
                warnings[key[0]].add('Warning: Unnecessary else clause at lineno %s in while loop at lineno %s' % key)
            for key in specific_checks.dangerous_defaults:
                warnings[key[3]].add('Warning: Dangerous default in fuction %s, with argument %s having default %s at lineno %s' % key)
            # for key, value in specific_checks.exception_does_nothing.items():
            #     warnings[value].add('Warning: Except doesn\'t do anything at lineno %s' % (value))
            for key in specific_checks.misplaced_imports:
                warnings[key].add('Warning: Misplaced import at lineno %s. Should be at the top of the file' % key)
            for key, value in specific_checks.specific_exceptions.items():
                warnings[value].add('Warning: Use of catch all exceptions at lineno %s. It is preferred to specify the type of the exception' % (value))
            for key, value in specific_checks.using_args_kwargs.items():
                warnings[value].add('Warning: Use of args or kwargs in arguments for function %s at lineno %s' % (key, value))
            for key in specific_checks.advisedNotUsedBuiltins:
                warnings[key[1]].add('Warning: Use of %s at lineno %s. It is advised not to call this function in your code' % (key[0], key[1]))
            for key, value in specific_checks.unreachable_lines.items():
                if value:
                    warnings[key[1]].add('Warning: unreachable lines in function %s at lineno(s) %s' % (key[0],value[0]))
            for key in class_checks.using_protected_members:
                warnings[key[2]].add('Warning: Object %s calling private member %s at lineno %s' % (key[1], key[0], key[2]))
            for key, value in class_checks.outside_attributes.items():
                warnings[key[2]].add('Warning: assign value %s in class %s outside of constructor at lineno %s' % (key[0], key[1], key[2]))
            for key, value in class_checks.redefined_new_class_attributes.items():
                for v in value:
                    warnings[v[1]].add('Warning: self attribute %s defined outside constructor in class %s at lineno %s' % (v[0], key[0], v[1]))
            for key, value in class_checks.static_method_selfs.items():
                warnings[key].add('Warning: Static method %s with %s as first argument at lineno %s' % (value[0], value[1], key))
            for key, value in class_checks.constructor_check.items():
                warnings[value].add('Warning: class %s is missing __init__ method at lineno %s' % (key, value))
            for key, value in class_checks.no_self_argument.items():
                warnings[value].add('Warning: function %s for class %s is missing the self or cls positional argument at lineno %s' % (key[0], key[1], value))
            for key, value in unused_arguments.unused_arguments.items():
                k = key[0]
                lineno = key[1]
                if value:
                    warnings[lineno].add('Warning: unused arguments %s found in function %s at lineno %s' % (value, k, lineno))
            for key, value in unused_imports.unused_imports.items():
                warnings[value].add('Warning: unused import %s at lineno %s' % (key, value) )
            for key,value in unused_variable.unused_names.items():
                for line_number in value:
                    warnings[line_number].add('Warning: unused variable name %s at lineno %s' % (key, line_number))
            for key,value in shadow_builtins.shadow_builtins.items():
                for builtin in value:
                    warnings[key].add('Warning: using python builtin function %s as variable at lineno %s' % (builtin, key))
            for key,value, in redefined_functions.redefined_functions.items():
                key = key[0].split('.')[-1]
                warnings[value].add('Warning: redefined function %s at lineno %s' % (key, value))
            if warnings:
                warnings_length = 0
                for key in warnings:
                    warnings_length += len(warnings[key])
                print('%s warning(s) found in code' % warnings_length)
                with open('warnings_file.txt', 'w') as f2:
                    for line_number in sorted(warnings.keys()):
                        for warning in warnings[line_number]:                              
                            s = '{} : {}'.format(line_number, warning)
                            print(s)
                            f2.write('{} : {}\n'.format(line_number, warning))
            print()
            ast.fix_missing_locations(tree)
            co = compile(tree, "<ast>", "exec")
            # exec(co)