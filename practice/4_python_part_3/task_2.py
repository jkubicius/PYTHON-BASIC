"""
Write function which executes custom operation from math module
for given arguments.
Restrition: math function could take 1 or 2 arguments
If given operation does not exists, raise OperationNotFoundException
Examples:
     >>> math_calculate('log', 1024, 2)
     10.0
     >>> math_calculate('ceil', 10.7)
     11
"""
import math

class OperationNotFoundException(Exception):
    pass

def math_calculate(function: str, *args):
    try:
        func = getattr(math, function)
        return func(*args)
    except AttributeError:
        raise OperationNotFoundException(f"Operation '{function}' not found.")

"""
Write tests for math_calculate function
"""
