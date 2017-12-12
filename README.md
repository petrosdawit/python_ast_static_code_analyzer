Project Description:
  Static Code Analyzer (python AST module)
  Inspired by already existing libraries (pylint, vulture)
  Code written in Python 3.6


How to run:
  This projects runs on any Python 3.x version
  To get the project working, download all the files and then run 'python main.py [file you are examining]'. Make sure you are within the compiler project folder when running.
  Demo_files is just a folder of files which have some sample demo files you can run with the project.
  
Warnings:  
- Unused variables
- Unused arguments
- Unused imports
- Redefined functions
- Shadowing builtins
- Attribute outside constructor
- No self/cls in class functions
- No __init__ methods
- Redefining name outside __init__
- Access to protected member of class
- Using bad functions like exec
- Unsatisfiable if and while conditions
- Static method with self/cls as first argument
- Unreachable code
- Exception types non-specified
- Except doesn’t do anything
- Used * or ** magic
- Dangerous defaults
- Unnecessary else in for loop
- Unnecessary while in for loop

  
Limitations:
- No inheritance, abstract classes (limited to one file b/c it is static code analysis)
- Some minor limitations in warnings, ex: Unreachable code (assignment to expression, value checking an imported value)
- No iterating with tuples as target. ex: for x,y in z.items()
- No assigning with targets or values as tuples. ex: x, y = 1, 2
- Strings as comments. ex: ''' string '''
- Naturally not checking for more potentially warnings (further testing to ensure all edge cases)

Future implementations:
- Utilize node.transformer for optimizations. ex: dead code removal
- Create database for nodes instead of reiterating through the ast 

