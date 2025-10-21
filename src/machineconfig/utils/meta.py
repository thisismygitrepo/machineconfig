"""Metaprogramming utilities for analyzing and serializing Python functions."""

from collections.abc import Callable
from typing import Any


def get_import_module_string(py_file: str):
    from machineconfig.scripts.python.helpers_fire.helpers4 import get_import_module_code
    from machineconfig.utils.accessories import get_repo_root
    from pathlib import Path
    repo_root = get_repo_root(Path(py_file))
    import_line = get_import_module_code(py_file)
    if repo_root is not None:
        repo_root_add = f"""sys.path.append(r'{repo_root}')"""
    else:
        repo_root_add = ""
    txt: str = f"""
try:
    {import_line}
except (ImportError, ModuleNotFoundError) as ex:
    print(fr"❌ Failed to import `{py_file}` as a module: {{ex}} ")
    print(fr"⚠️ Attempting import with ad-hoc `$PATH` manipulation. DO NOT pickle any objects in this session as correct deserialization cannot be guaranteed.")
    import sys
    sys.path.append(r'{Path(py_file).parent}')
    {repo_root_add}
    from {Path(py_file).stem} import *
    print(fr"✅ Successfully imported `{py_file}`")
"""
    return txt


def lambda_to_python_script(lmb: Callable[[], Any], in_global: bool, import_module: bool) -> str:
    """
    caveats: always use keyword arguments in the lambda call for best results.
    return statement not allowed in the wrapped function (otherwise it can be put in the global space)
    type hint in kwargs has nothing that is not built in, e.g. Optional will not work as it requires an import.

    Given a no-arg lambda like `lambda: func(a=var1, b=var2)`,
    return a string containing the full function definition of `func`
    but with the defaults for the parameters provided in the call replaced
    by the *actual* values (repr) taken from the lambda's globals.

    All imports are local to this function.
    
    Args:
        lmb: A lambda function with no arguments
        in_global: If True, return kwargs as global variable assignments followed by dedented body.
                   If False, return the full function definition with updated defaults.
        import_module: When True, prepend module import bootstrap code for the function's source file.
    """
    # local imports
    import inspect as _inspect
    import ast as _ast
    import textwrap as _textwrap
    import types as _types
    from pathlib import Path as _Path

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

    import_prefix: str = ""
    if import_module:
        module_file = _inspect.getsourcefile(func_obj)
        module_path_candidate: str = module_file if module_file is not None else _inspect.getfile(func_obj)
        import_prefix = get_import_module_string(str(_Path(module_path_candidate)))

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
            result_parts: list[str] = ["\n".join(global_assignments), "", dedented_body]
            result_text = "\n".join(result_parts)
        else:
            result_text = dedented_body
    else:
        header = f"def {func_name}{new_sig}:\n"
        result_text = header + body_text

    if import_prefix:
        return f"{import_prefix}{result_text}"
    return result_text


if __name__ == "__main__":
    pass
