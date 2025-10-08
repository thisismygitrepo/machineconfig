"""Metaprogramming utilities for analyzing and serializing Python functions."""

import ast
import inspect
import textwrap
from types import FunctionType, ModuleType
from typing import Any


def function_to_script(func: FunctionType, call_with_args: tuple[Any, ...] | None = None, call_with_kwargs: dict[str, Any] | None = None) -> str:
    """Convert a function to a standalone executable Python script.
    
    This function analyzes a given function and generates a complete Python script
    that includes all necessary imports, global variables, the function definition,
    and optionally a function call.
    
    Args:
        func: The function to convert to a script
        call_with_args: Optional tuple of positional arguments to call the function with
        call_with_kwargs: Optional dict of keyword arguments to call the function with
    
    Returns:
        A complete Python script as a string that can be executed independently
    
    Raises:
        ValueError: If the function cannot be inspected or analyzed
    """
    if not callable(func) or not hasattr(func, '__code__'):
        raise ValueError(f"Expected a function, got {type(func)}")
    
    call_with_args = call_with_args or ()
    call_with_kwargs = call_with_kwargs or {}
    
    imports = _extract_imports(func)
    globals_needed = _extract_globals(func)
    source_code = _get_function_source(func)
    call_statement = _generate_call_statement(func, call_with_args, call_with_kwargs)
    
    script_parts: list[str] = []
    
    if imports:
        script_parts.append(imports)
        script_parts.append("")
    
    if globals_needed:
        script_parts.append(globals_needed)
        script_parts.append("")
    
    script_parts.append(source_code)
    script_parts.append("")
    
    if call_statement:
        script_parts.append("")
        script_parts.append("if __name__ == '__main__':")
        script_parts.append(f"    {call_statement}")
    
    return "\n".join(script_parts)


def _get_function_source(func: FunctionType) -> str:
    """Extract the source code of a function."""
    try:
        source = inspect.getsource(func)
        return textwrap.dedent(source)
    except (OSError, TypeError) as e:
        raise ValueError(f"Cannot get source code for function {func.__name__}: {e}") from e


def _extract_imports(func: FunctionType) -> str:
    """Extract all import statements needed by the function."""
    import_statements: set[str] = set()
    
    source = _get_function_source(func)
    func_globals = func.__globals__
    
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        raise ValueError(f"Failed to parse function source: {e}") from e
    
    used_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used_names.add(node.id)
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                used_names.add(node.value.id)
    
    for name in used_names:
        if name in func_globals:
            obj = func_globals[name]
            
            if isinstance(obj, ModuleType):
                module_name = obj.__name__
                if name == module_name.split('.')[-1]:
                    import_statements.add(f"import {module_name}")
                else:
                    import_statements.add(f"import {module_name} as {name}")
            
            elif hasattr(obj, '__module__') and obj.__module__ != '__main__':
                try:
                    module_name = obj.__module__
                    obj_name = obj.__name__ if hasattr(obj, '__name__') else name
                    
                    if module_name and module_name != 'builtins':
                        if obj_name == name:
                            import_statements.add(f"from {module_name} import {obj_name}")
                        else:
                            import_statements.add(f"from {module_name} import {obj_name} as {name}")
                except AttributeError:
                    pass
    
    return "\n".join(sorted(import_statements))


def _extract_globals(func: FunctionType) -> str:
    """Extract global variables needed by the function."""
    global_assignments: list[str] = []
    
    source = _get_function_source(func)
    func_globals = func.__globals__
    
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        raise ValueError(f"Failed to parse function source: {e}") from e
    
    used_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used_names.add(node.id)
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                used_names.add(node.value.id)
    
    for name in used_names:
        if name in func_globals:
            obj = func_globals[name]
            
            if not isinstance(obj, (ModuleType, FunctionType, type)):
                if not (hasattr(obj, '__module__') and hasattr(obj, '__name__')):
                    try:
                        repr_str = repr(obj)
                        if len(repr_str) < 1000 and '\n' not in repr_str:
                            global_assignments.append(f"{name} = {repr_str}")
                    except Exception:
                        global_assignments.append(f"# Warning: Could not serialize global variable '{name}'")
    
    return "\n".join(global_assignments)


def _generate_call_statement(func: FunctionType, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    """Generate a function call statement with the given arguments."""
    if not args and not kwargs:
        return f"{func.__name__}()"
    
    arg_parts: list[str] = []
    
    for arg in args:
        arg_parts.append(repr(arg))
    
    for key, value in kwargs.items():
        arg_parts.append(f"{key}={repr(value)}")
    
    args_str = ", ".join(arg_parts)
    return f"{func.__name__}({args_str})"
