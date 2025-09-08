# from pathlib import Path
# from machineconfig.utils.path_reduced import P as PathExtended
# from machineconfig.utils.io_save import save_pickle
# from plotly import graph_objects as go
# import plotly.express as px
# from typing import Callable, Iterable, Any, Optional

# def default_get_figure(data: Any) -> go.Figure:
#     print("📊 Generating default figure using Plotly...")
#     return px.line(data)

# default_streamlit_config = """

# [server]
# headless = true
# port = 4614

# """

# def run(data: Optional[Iterable[Any]], data_path: Optional[str],
#         get_figure: Optional[Callable[[Any], go.Figure]]):
#     print("\n" + "=" * 50)
#     print("👁️  Welcome to the Data Viewer Tool")
#     print("=" * 50 + "\n")

#     print("📂 Preparing viewer application...")
#     code = PathExtended(__file__).parent.joinpath("viewer_template.py").read_text(encoding='utf-8')

#     code_dir = PathExtended.tmpdir(prefix="viewer")
#     code_dir.joinpath(".streamlit").mkdir(parents=True, exist_ok=False)
#     code_dir.joinpath(".streamlit/config.toml").write_text(default_streamlit_config, encoding='utf-8')

#     if data_path is None:
#         print("💾 Saving data to temporary path...")
#         data_path = str(save_pickle(obj=data, path=code_dir.joinpath("data.pkl")))

#     code = code.replace("""data_path = \"get_figure_placeholder.pkl\" """, f"""data_path = r"{data_path}" """)

#     import inspect
#     if get_figure is None:
#         print("📊 Using default figure generation function.")
#         get_figure = default_get_figure

#     code_func = inspect.getsource(get_figure)
#     code_parts = code.split("# get_figure_placeholder")
#     code = code_parts[0] + code_func + f"""\nget_figure = {get_figure.__name__}""" + code_parts[-1]

#     code_path = code_dir.joinpath("viewer_app.py")
#     Path(code_path).write_text(code, encoding='utf-8')

#     print("✅ Viewer application prepared successfully!")
#     print(f"📂 Application files saved to: {code_dir}\n")

#     return code_path
