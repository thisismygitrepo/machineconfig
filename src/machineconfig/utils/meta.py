"""Metaprogramming utilities for analyzing and serializing Python functions."""

import ast
import inspect
import textwrap
from collections.abc import Callable, Mapping
from types import FunctionType, ModuleType
from typing import ParamSpec

P = ParamSpec("P")


def function_to_script(func: Callable[P, object], call_with_kwargs: Mapping[str, object] | None) -> str:
    """Convert a function to a standalone executable Python script.
    
    This function analyzes a given function and generates a complete Python script
    that includes all necessary imports, global variables, the function definition,
    and optionally a function call.
    
    Args:
        func: The function to convert to a script
        call_with_kwargs: Optional dict of keyword arguments to call the function with
    
    Returns:
        A complete Python script as a string that can be executed independently
    
    Raises:
        ValueError: If the function cannot be inspected or analyzed
    """
    if not isinstance(func, FunctionType):
        raise ValueError(f"""Expected a Python function, got {type(func)}""")

    python_func = func

    imports = _extract_imports(python_func)
    globals_needed = _extract_globals(python_func)
    source_code = _get_function_source(python_func).rstrip()
    validated_kwargs = _prepare_call_kwargs(python_func, call_with_kwargs)
    call_statement = _generate_call_statement(python_func, validated_kwargs) if validated_kwargs is not None else None

    script_parts: list[str] = []

    if imports:
        script_parts.append(imports)

    if globals_needed:
        if script_parts:
            script_parts.append("")
        script_parts.append(globals_needed)

    if script_parts:
        script_parts.append("")

    script_parts.append(source_code)

    if call_statement is not None:
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


def _prepare_call_kwargs(func: FunctionType, call_with_kwargs: Mapping[str, object] | None) -> dict[str, object] | None:
    if call_with_kwargs is None:
        return None

    normalized_kwargs = dict(call_with_kwargs)

    if not normalized_kwargs:
        return {}

    signature = inspect.signature(func)
    positional_only = [parameter.name for parameter in signature.parameters.values() if parameter.kind is inspect.Parameter.POSITIONAL_ONLY]

    if positional_only:
        joined = ", ".join(positional_only)
        raise ValueError(f"""Cannot call {func.__name__} with positional-only parameters: {joined}""")

    try:
        signature.bind(**normalized_kwargs)
    except TypeError as error:
        raise ValueError(f"""Invalid call_with_kwargs for {func.__name__}: {error}""") from error

    return normalized_kwargs


def _generate_call_statement(func: FunctionType, kwargs: dict[str, object]) -> str:
    """Generate a function call statement with the given keyword arguments."""
    if not kwargs:
        return f"{func.__name__}()"

    arg_parts: list[str] = [f"{key}={repr(value)}" for key, value in kwargs.items()]
    args_str = ", ".join(arg_parts)
    return f"{func.__name__}({args_str})"


if __name__ == "__main__":
    # Example usage
    a = True
    b = 3
    def func(no_copy_assets: bool = a):
        from machineconfig.scripts.python.helpers_devops.cli_self import update
        update(no_copy_assets=no_copy_assets)
    script = function_to_script(func, call_with_kwargs=None)
    print(script)
    pass
