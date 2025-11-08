
from typing import TYPE_CHECKING, Annotated
from git import Repo
from collections import defaultdict
from datetime import datetime

from pathlib import Path
from rich.console import Console
from rich.progress import track
from rich.table import Table
import typer


if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Union
    import polars as pl


def count_lines_in_commit(commit: "Any") -> int:
    _total_lines = 0
    for _file in commit.stats.files:
        if str(_file).endswith(".py"):
            _blob = commit.tree / _file
            _total_lines += len(_blob.data_stream.read().decode("utf-8").splitlines())
    return _total_lines


def count_historical_loc(repo_path: str) -> int:
    repo = Repo(repo_path)
    file_line_counts: "Dict[str, int]" = defaultdict(int)
    total_commits: int = sum(1 for _ in repo.iter_commits())
    print(f"Total commits to process: {total_commits}")
    for i, commit in enumerate(repo.iter_commits(), 1):
        if i % 100 == 0 or i == total_commits:
            print(f"Processing commit {i}/{total_commits} ({i / total_commits:.1%})")
        try:
            # Handle initial commits that have no parents
            if not commit.parents:
                # For initial commit, count all lines in Python files
                for file in commit.stats.files:
                    if str(file).endswith(".py"):
                        file_line_counts[str(file)] += commit.stats.files[file]["insertions"]
            else:
                # For commits with parents, use stats
                for file in commit.stats.files:
                    if str(file).endswith(".py"):
                        file_line_counts[str(file)] += commit.stats.files[file]["insertions"]
        except Exception:
            # If stats fail (e.g., corrupted parent), skip this commit
            print(f"Warning: Could not get stats for commit {commit.hexsha[:8]}, skipping")
            continue

    print(f"\nProcessed files: {len(file_line_counts)}")
    return sum(file_line_counts.values())

def count_python_lines(commit: "Any") -> int:
    """Count total lines in Python files for a specific commit"""
    total_lines = 0
    try:
        for blob in commit.tree.traverse():
            if blob.path.endswith(".py"):
                try:
                    content = blob.data_stream.read().decode("utf-8")
                    total_lines += len(content.splitlines())
                except Exception as _e:
                    continue
    except Exception as _e:
        return 0
    return total_lines
def get_default_branch(repo: Repo) -> str:
    """Get the default branch name of the repository"""
    try:
        _ = repo.refs["main"]
        return "main"  # First try 'main'
    except IndexError:
        try:
            _ = repo.refs["master"]
            return "master"  # Then try 'master'
        except IndexError:
            return repo.head.reference.name  # If neither exists, get the branch the HEAD is pointing to



console = Console()


def count_historical(repo_path: Annotated[str, typer.Argument(..., help="Path to the git repository")]):
    """Count total historical lines of Python code in the repository."""
    print(f"Analyzing repository: {repo_path}")
    total_loc: int = count_historical_loc(repo_path)
    print(f"\nTotal historical lines of Python code: {total_loc}")



def analyze_over_time(repo_path: Annotated[str, typer.Argument(..., help="Path to the git repository")]):
    """Analyze a git repository to track Python code size over time with visualization."""
    repo: Repo = Repo(repo_path)
    branch_name: str = get_default_branch(repo)
    print(f"🔍 Using branch: {branch_name}")
    commit_data: "List[Dict[str, Any]]" = []
    print("⏳ Analyzing commits...")
    try:
        commits = list(repo.iter_commits(branch_name))
        from datetime import timezone

        for commit in track(commits, description="Processing commits..."):
            commit_data.append({"hash": commit.hexsha, "dtmExit": datetime.fromtimestamp(commit.committed_date, tz=timezone.utc), "lines": count_python_lines(commit)})
    except Exception as e:
        print(f"❌ Error analyzing commits: {str(e)}")
        return

    import polars as pl
    import plotly.graph_objects as go

    df = pl.DataFrame(commit_data)
    df = df.sort("dtmExit")
    # Create interactive plotly figure with dark theme and all bells and whistles
    fig = go.Figure()
    # Add line chart with gradient fill and sparkle effect
    fig.add_trace(go.Scatter(x=df["dtmExit"], y=df["lines"], mode="lines", line={"width": 3, "color": "#00b4ff"}, fill="tozeroy", fillcolor="rgba(0, 180, 255, 0.2)", name="Lines of Code", hovertemplate="<b>Date:</b> %{x}<br><b>Lines:</b> %{y:,}<extra></extra>"))
    # Add markers for significant points (min, max, last)
    min_idx = df["lines"].arg_min()
    max_idx = df["lines"].arg_max()
    min_point = df.slice(min_idx, 1).to_dicts()[0] if min_idx is not None else {}
    max_point = df.slice(max_idx, 1).to_dicts()[0] if max_idx is not None else {}
    last_point = df.slice(-1, 1).to_dicts()[0]

    # Add markers for significant points
    fig.add_trace(
        go.Scatter(
            x=[min_point["dtmExit"], max_point["dtmExit"], last_point["dtmExit"]],
            y=[min_point["lines"], max_point["lines"], last_point["lines"]],
            mode="markers",
            marker={"size": [10, 14, 12], "color": ["#ff4f4f", "#4fff4f", "#4f4fff"], "line": {"width": 2, "color": "white"}, "symbol": ["circle", "star", "diamond"]},
            name="Key Points",
            hovertemplate="<b>%{text}</b><br>Date: %{x}<br>Lines: %{y:,}<extra></extra>",
            text=[f"🔽 Min: {min_point['lines']:,} lines", f"🔼 Max: {max_point['lines']:,} lines", f"📊 Current: {last_point['lines']:,} lines"],
        )
    )

    # Add annotation only for current point
    # annotations = [
    #     {"x": last_point['date'], "y": last_point['lines'], "text": f"📊 Current: {last_point['lines']:,} lines", "showarrow": True, "arrowhead": 2, "arrowsize": 1,
    #         "arrowwidth": 2, "arrowcolor": "#ffffff", "font": {"size": 14, "color": "#ffffff"}, "bgcolor": "#00b4ff", "bordercolor": "#ffffff",
    #         "borderwidth": 1, "borderpad": 4, "ax": 40, "ay": -40}
    # ]

    # Update layout with dark theme and customizations
    fig.update_layout(
        title={"text": "✨ Python Code Base Size Over Time ✨", "y": 0.95, "x": 0.5, "xanchor": "center", "yanchor": "top", "font": {"size": 24, "color": "white"}},
        xaxis_title="Date 📅",
        yaxis_title="Lines of Code 📝",
        hovermode="closest",
        template="plotly_dark",
        plot_bgcolor="rgba(25, 25, 35, 1)",
        paper_bgcolor="rgba(15, 15, 25, 1)",
        font={"family": "Arial, sans-serif", "size": 14, "color": "white"},  # annotations=annotations,
        autosize=True,
        height=700,
        margin={"l": 80, "r": 80, "t": 100, "b": 80},
        xaxis={"showgrid": True, "gridcolor": "rgba(80, 80, 100, 0.2)", "showline": True, "linecolor": "rgba(200, 200, 255, 0.2)", "tickfont": {"size": 12}},
        yaxis={"showgrid": True, "gridcolor": "rgba(80, 80, 100, 0.2)", "showline": True, "linecolor": "rgba(200, 200, 255, 0.2)", "tickformat": ",", "tickfont": {"size": 12}},
    )

    # Add range slider for date selection
    fig.update_xaxes(rangeslider_visible=True, rangeslider_thickness=0.05)

    # Save as interactive HTML and static image
    plot_dir = Path.home().joinpath("tmp_results", "tmp_images", Path(repo_path).name)
    plot_dir.mkdir(parents=True, exist_ok=True)

    html_path = plot_dir.joinpath("code_size_evolution.html")
    png_path = plot_dir.joinpath("code_size_evolution.png")

    try:
        fig.write_html(html_path, include_plotlyjs="cdn")
    except Exception as e:
        print(f"❌ Error saving HTML plot: {str(e)}")
    try:
        fig.write_image(png_path, width=1200, height=700, scale=2)
    except Exception as e:
        print(f"❌ Error saving PNG plot: {str(e)}")

    print(f"🖼️ Interactive plot saved as {html_path}")
    print(f"🖼️ Static image saved as {png_path}")
    # Print statistics
    print("\n📊 Repository Statistics:")
    print(f"📚 Total commits analyzed: {len(df)}")
    print(f"🔙 Initial line count: {df['lines'][-1]:,}")
    print(f"🔜 Final line count: {df['lines'][0]:,}")
    print(f"📈 Net change: {df['lines'][0] - df['lines'][-1]:,} lines")


def _print_python_files_by_size_impl(repo_path: str) -> "Union[pl.DataFrame, Exception]":
    import polars as pl
    import plotly.graph_objects as go
    import plotly.express as px

    try:
        import os
        if not os.path.exists(repo_path):
            return ValueError(f"Repository path does not exist: {repo_path}")
        # Initialize data storage
        file_data: "List[Dict[str, Union[str, int]]]" = []

        # Walk through the repository
        for root, _, files in os.walk(repo_path):
            # Skip .git directory and other hidden directories
            if ".git" in Path(root).parts or any(part.startswith(".") for part in Path(root).parts):
                continue

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        # Count lines in the file
                        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                            line_count = sum(1 for _ in f)

                        # Make path relative to repo_path for better display
                        rel_path = os.path.relpath(file_path, repo_path)
                        file_data.append({"filename": rel_path, "lines": line_count})
                    except Exception as e:
                        print(f"⚠️ Warning: Could not read {file_path}: {str(e)}")
                        continue

        # Check if any files were found
        if not file_data:
            return ValueError("❌ No Python files found in the repository")

        # Convert to DataFrame
        df = pl.DataFrame(file_data)

        # Sort DataFrame by line count (descending)
        df = df.sort("lines", descending=True)
        df = df.filter(pl.col("lines") > 0)  # Filter out empty files

        # Add total count
        total_lines = int(df["lines"].sum())
        file_count: int = len(df)

        # Print the DataFrame
        console.print("\n📊 Python Files Line Count (sorted max to min):")

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("#", justify="right")
        table.add_column("File", overflow="fold")
        table.add_column("Lines", justify="right")

        for idx, row in enumerate(df.iter_rows(named=True), 1):
            table.add_row(str(idx), row["filename"], f"{row['lines']:,}")

        console.print(table)
        print(f"\n📁 Total Python files: {file_count}")
        print(f"📝 Total lines of Python code: {total_lines:,}")

        # Create visualizations with Plotly
        # Only visualize top files (too many files make the chart unreadable)
        top_n: int = min(20, len(df))
        top_files_df = df.head(top_n).clone()

        # Calculate percentage of total for top files
        top_files_df = top_files_df.with_columns((pl.col("lines") / total_lines * 100).round(1).alias("percentage"))

        # Shorten filenames for better display
        import os

        top_files_df = top_files_df.with_columns(pl.col("filename").map_elements(lambda x: os.path.basename(x) if len(x) > 25 else x, return_dtype=pl.Utf8).alias("short_name"))

        # Create bar chart with hover info showing full path
        fig = go.Figure()

        # Add bars with gradient color based on line count
        fig.add_trace(
            go.Bar(
                x=top_files_df["short_name"].to_list(),
                y=top_files_df["lines"].to_list(),
                text=[f"{x}%" for x in top_files_df["percentage"].to_list()],
                textposition="auto",
                hovertemplate="<b>%{customdata}</b><br>Lines: %{y:,}<br>Percentage: %{text}<extra></extra>",
                customdata=top_files_df["filename"],
                marker={"color": top_files_df["lines"], "colorscale": "Viridis", "showscale": True, "colorbar": {"title": "Lines", "thickness": 20, "tickformat": ","}, "line": {"width": 1, "color": "white"}},
                opacity=0.9,
            )
        )

        # Update layout with dark theme
        fig.update_layout(
            title={"text": f"🏆 Top {top_n} Python Files by Size", "y": 0.95, "x": 0.5, "xanchor": "center", "yanchor": "top", "font": {"size": 24, "color": "white"}},
            xaxis_title="File Name 📄",
            yaxis_title="Lines of Code 📝",
            template="plotly_dark",
            plot_bgcolor="rgba(25, 25, 35, 1)",
            paper_bgcolor="rgba(15, 15, 25, 1)",
            font={"family": "Arial, sans-serif", "size": 14, "color": "white"},
            height=700,
            margin={"l": 80, "r": 80, "t": 100, "b": 100},
            xaxis={"tickangle": 45, "showgrid": False, "showline": True, "linecolor": "rgba(200, 200, 255, 0.2)", "tickfont": {"size": 12}},
            yaxis={"showgrid": True, "gridcolor": "rgba(80, 80, 100, 0.2)", "showline": True, "linecolor": "rgba(200, 200, 255, 0.2)", "tickformat": ",", "tickfont": {"size": 12}},
        )

        # Define pie chart figure before conditionally using it
        fig2: "Optional[go.Figure]" = None

        # Add pie chart showing distribution
        if len(df) > top_n:
            # Prepare data for pie chart - top files plus "Others"
            others_lines = df.slice(top_n)["lines"].sum()
            pie_labels = list(top_files_df["short_name"]) + ["Others"]
            pie_values = list(top_files_df["lines"]) + [others_lines]
            pie_customdata = list(top_files_df["filename"]) + [f"Other {len(df) - top_n} files"]

            fig2 = go.Figure()
            fig2.add_trace(go.Pie(labels=pie_labels, values=pie_values, customdata=pie_customdata, textinfo="percent", hovertemplate="<b>%{customdata}</b><br>Lines: %{value:,}<br>Percentage: %{percent}<extra></extra>", marker={"colors": px.colors.sequential.Viridis, "line": {"color": "white", "width": 1}}, hole=0.4, sort=False))

            fig2.update_layout(
                title={"text": "🍩 Python Code Distribution by File", "y": 0.95, "x": 0.5, "xanchor": "center", "yanchor": "top", "font": {"size": 24, "color": "white"}},
                template="plotly_dark",
                plot_bgcolor="rgba(25, 25, 35, 1)",
                paper_bgcolor="rgba(15, 15, 25, 1)",
                font={"family": "Arial, sans-serif", "size": 14, "color": "white"},
                height=700,
                annotations=[{"text": f"Total<br>{total_lines:,}<br>lines", "x": 0.5, "y": 0.5, "font": {"size": 18, "color": "white"}, "showarrow": False}],
            )

        # Save visualizations
        plot_dir = Path.home().joinpath("tmp_results", "tmp_images", Path(repo_path).name)
        plot_dir.mkdir(parents=True, exist_ok=True)

        # Bar chart
        bar_html_path = plot_dir.joinpath("top_files_by_size.html")
        bar_png_path = plot_dir.joinpath("top_files_by_size.png")
        fig.write_html(bar_html_path, include_plotlyjs="cdn")
        fig.write_image(bar_png_path, width=1200, height=700, scale=2)

        print(f"\n🖼️ Interactive bar chart saved as {bar_html_path}")
        print(f"🖼️ Static bar chart saved as {bar_png_path}")

        # Pie chart if available
        if fig2 is not None:
            pie_html_path = plot_dir.joinpath("files_distribution_pie.html")
            pie_png_path = plot_dir.joinpath("files_distribution_pie.png")
            fig2.write_html(pie_html_path, include_plotlyjs="cdn")
            fig2.write_image(pie_png_path, width=1200, height=700, scale=2)

            print(f"🖼️ Interactive pie chart saved as {pie_html_path}")
            print(f"🖼️ Static pie chart saved as {pie_png_path}")

        return df

    except Exception as e:
        return Exception(f"❌ Error analyzing repository: {str(e)}")



def print_python_files_by_size(repo_path: Annotated[str, typer.Argument(..., help="Path to the git repository")]):
    """Print Python files sorted by size with visualizations."""
    result = _print_python_files_by_size_impl(repo_path)
    if isinstance(result, Exception):
        print(f"Error: {result}")
        return


def get_app():
    app = typer.Typer()
    app.command(name="count-historical", no_args_is_help=True, help="[c] Count lines of code in a git repository")(count_historical)
    app.command(name="c", hidden=True, no_args_is_help=True, help="Alias for count-historical")(count_historical)
    app.command(name="analyze-over-time", no_args_is_help=True, help="[a] Analyze code size over time in a git repository")(analyze_over_time)
    app.command(name="a", hidden=True, no_args_is_help=True, help="Alias for analyze-over-time")(analyze_over_time)
    app.command(name="print-python-files-by-size", no_args_is_help=True, help="[p] Print Python files by size in a git repository")(print_python_files_by_size)
    app.command(name="p", hidden=True, no_args_is_help=True, help="Alias for print-python-files-by-size")(print_python_files_by_size)
    return app


if __name__ == "__main__":
    get_app()()

