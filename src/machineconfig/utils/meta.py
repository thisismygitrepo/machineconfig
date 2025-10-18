"""Metaprogramming utilities for analyzing and serializing Python functions."""

import ast
import inspect
import textwrap
from collections.abc import Callable, Mapping
from types import FunctionType, ModuleType
from typing import Any, ParamSpec

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
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for default in node.args.defaults + node.args.kw_defaults:
                if default is not None:
                    for subnode in ast.walk(default):
                        if isinstance(subnode, ast.Name):
                            used_names.add(subnode.id)
                        elif isinstance(subnode, ast.Attribute):
                            if isinstance(subnode.value, ast.Name):
                                used_names.add(subnode.value.id)
    
    for name in used_names:
        if name in func_globals:
            obj = func_globals[name]
            
            if isinstance(obj, ModuleType):
                module_name = obj.__name__
                if name == module_name.split('.')[-1]:
                    import_statements.add(f"import {module_name}")
                else:
                    import_statements.add(f"import {module_name} as {name}")
            
            elif isinstance(obj, type) and hasattr(obj, '__module__') and obj.__module__ != '__main__':
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
            
            elif callable(obj) and not isinstance(obj, type) and hasattr(obj, '__module__') and obj.__module__ != '__main__':
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
    needed_types: set[type] = set()
    
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
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for default in node.args.defaults + node.args.kw_defaults:
                if default is not None:
                    for subnode in ast.walk(default):
                        if isinstance(subnode, ast.Name):
                            used_names.add(subnode.id)
                        elif isinstance(subnode, ast.Attribute):
                            if isinstance(subnode.value, ast.Name):
                                used_names.add(subnode.value.id)
    
    for name in used_names:
        if name in func_globals:
            obj = func_globals[name]
            
            if not isinstance(obj, (ModuleType, FunctionType, type)):
                if not (hasattr(obj, '__module__') and hasattr(obj, '__name__')):
                    try:
                        obj_type = type(obj)
                        
                        if obj_type.__name__ == 'PathExtended' and obj_type.__module__ == 'machineconfig.utils.path_extended':
                            global_assignments.append(f"{name} = PathExtended('{str(obj)}')")
                            if obj_type.__module__ not in ['builtins', '__main__']:
                                needed_types.add(obj_type)
                        else:
                            repr_str = repr(obj)
                            if len(repr_str) < 1000 and '\n' not in repr_str and all(ord(c) < 128 or c in [' ', '\n', '\t'] for c in repr_str):
                                global_assignments.append(f"{name} = {repr_str}")
                                if obj_type.__module__ not in ['builtins', '__main__']:
                                    needed_types.add(obj_type)
                            else:
                                global_assignments.append(f"# Warning: Could not serialize global variable '{name}' (repr too complex or contains non-ASCII)")
                    except Exception as e:
                        global_assignments.append(f"# Warning: Could not serialize global variable '{name}': {e}")
    
    result_parts: list[str] = []
    
    if needed_types:
        for obj_type in sorted(needed_types, key=lambda t: (t.__module__, t.__name__)):
            module_name = obj_type.__module__
            type_name = obj_type.__name__
            result_parts.append(f"from {module_name} import {type_name}")
        result_parts.append("")
    
    result_parts.extend(global_assignments)
    
    return "\n".join(result_parts)


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


def lambda_to_defstring(lmb: Callable[[], Any], in_global: bool = False) -> str:
    """
    Given a no-arg lambda like `lambda: func(a=var1, b=var2)`,
    return a string containing the full function definition of `func`
    but with the defaults for the parameters provided in the call replaced
    by the *actual* values (repr) taken from the lambda's globals.

    All imports are local to this function.
    
    Args:
        lmb: A lambda function with no arguments
        in_global: If True, return kwargs as global variable assignments followed by dedented body.
                   If False (default), return the full function definition with updated defaults.
    """
    # local imports
    import inspect as _inspect
    import ast as _ast
    import textwrap as _textwrap
    import types as _types

    # sanity checks
    if not (callable(lmb) and isinstance(lmb, _types.LambdaType)):
        raise TypeError("Expected a lambda function object")

    src = _inspect.getsource(lmb)
    src = _textwrap.dedent(src)
    tree = _ast.parse(src)

    # find first Lambda node
    lambda_node = None
    for n in _ast.walk(tree):
        if isinstance(n, _ast.Lambda):
            lambda_node = n
            break
    if lambda_node is None:
        raise ValueError("Could not find a lambda expression in source")

    body = lambda_node.body
    if not isinstance(body, _ast.Call):
        raise ValueError("Lambda body is not a call expression")

    globals_dict = getattr(lmb, "__globals__", {})
    
    # Also capture closure variables from the lambda
    closure_dict: dict[str, Any] = {}
    if lmb.__closure__:
        code_obj = lmb.__code__
        freevars = code_obj.co_freevars
        for i, var_name in enumerate(freevars):
            closure_dict[var_name] = lmb.__closure__[i].cell_contents
    
    # Merge globals and closures (closures take precedence for shadowing)
    eval_namespace = {**globals_dict, **closure_dict}

    # resolve the function object being called
    try:
        func_ref_src = _ast.unparse(body.func)
    except AttributeError:
        func_ref_src = _ast.get_source_segment(src, body.func) or ""
    try:
        func_obj = eval(func_ref_src, eval_namespace)
    except Exception as e:
        raise RuntimeError(f"Could not resolve function reference '{func_ref_src}': {e}")

    if not callable(func_obj):
        raise TypeError("Resolved object is not callable")

    func_name = getattr(func_obj, "__name__", "<unknown>")

    # Evaluate each keyword argument value in the lambda's globals to get real Python objects
    call_kwargs = {}
    for kw in body.keywords:
        if kw.arg is None:
            # **kwargs in call — evaluate to dict and merge
            try:
                val = eval(compile(_ast.Expression(kw.value), "<lambda_eval>", "eval"), eval_namespace)
                if isinstance(val, dict):
                    call_kwargs.update(val)
                else:
                    raise ValueError("Keyword expansion did not evaluate to a dict")
            except Exception as e:
                raise RuntimeError(f"Failed to evaluate **kwargs expression: {e}")
        else:
            try:
                val = eval(compile(_ast.Expression(kw.value), "<lambda_eval>", "eval"), eval_namespace)
                call_kwargs[kw.arg] = val
            except Exception as e:
                raise RuntimeError(f"Failed to evaluate value for kw '{kw.arg}': {e}")

    # Try to get original source and dedent it for body extraction
    try:
        orig_src = _inspect.getsource(func_obj)
        ded = _textwrap.dedent(orig_src)
        lines = ded.splitlines()
        # find the line that starts with def <name>(
        def_index = None
        for i, ln in enumerate(lines):
            if ln.lstrip().startswith(f"def {func_name}("):
                def_index = i
                break
        if def_index is None:
            body_lines = ded.splitlines()
        else:
            body_lines = lines[def_index + 1 :]
        # ensure we have a body, otherwise use pass
        if not any(line.strip() for line in body_lines):
            body_text = "    pass\n"
        else:
            # keep the dedented body lines exactly as-is (they should be indented)
            body_text = "\n".join(body_lines) + ("\n" if not body_lines[-1].endswith("\n") else "")
    except (OSError, IOError, TypeError):
        body_text = "    pass\n"

    # Build a replaced signature using inspect.signature
    sig = _inspect.signature(func_obj)
    new_params = []
    for name, param in sig.parameters.items():
        # If the call provided a value for this parameter, replace default
        if name in call_kwargs:
            new_default = call_kwargs[name]
        else:
            new_default = param.default

        # Recreate the Parameter (keeping annotation and kind)
        if new_default is _inspect.Parameter.empty:
            new_param = _inspect.Parameter(name, param.kind, annotation=param.annotation)
        else:
            new_param = _inspect.Parameter(
                name, param.kind, default=new_default, annotation=param.annotation
            )
        new_params.append(new_param)

    new_sig = _inspect.Signature(parameters=new_params, return_annotation=sig.return_annotation)

    # If in_global mode, return kwargs as global assignments + dedented body
    if in_global:
        global_assignments: list[str] = []
        for name, param in sig.parameters.items():
            # Get the value from call_kwargs if provided, else use original default
            if name in call_kwargs:
                value = call_kwargs[name]
            elif param.default is not _inspect.Parameter.empty:
                value = param.default
            else:
                # No value provided and no default - skip this parameter
                continue
            
            # Build type annotation string if available
            if param.annotation is not _inspect.Parameter.empty:
                # Try to get a nice string representation of the annotation
                try:
                    if hasattr(param.annotation, "__name__"):
                        type_str = param.annotation.__name__
                    else:
                        type_str = str(param.annotation)
                except Exception:
                    type_str = str(param.annotation)
                global_assignments.append(f"{name}: {type_str} = {repr(value)}")
            else:
                global_assignments.append(f"{name} = {repr(value)}")
        
        # Dedent the body text to remove function indentation
        dedented_body = _textwrap.dedent(body_text).rstrip()
        
        # Combine global assignments and body
        if global_assignments:
            result_parts = ["\n".join(global_assignments), "", dedented_body]
            return "\n".join(result_parts)
        else:
            return dedented_body

    # Compose final function definition text
    header = f"def {func_name}{new_sig}:\n"
    final_src = header + body_text
    return final_src


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
