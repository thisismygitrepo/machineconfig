# #!/usr/bin/env python3
# from pathlib import Path
# from typing import Annotated
# import subprocess
# import typer
# from rich.console import Console
# from rich.progress import Progress, SpinnerColumn, TextColumn
# from rich.table import Table
# from rich.syntax import Syntax

# import chromadb
# from chromadb.config import Settings
# from sentence_transformers import SentenceTransformer


# app = typer.Typer(help="Semantic search over your repository using local RAG")
# console = Console()


# DEFAULT_EXTENSIONS = [".py", ".sh", ".ps1", ".md", ".toml", ".yaml", ".yml", ".json"]
# DEFAULT_MODEL = "all-MiniLM-L6-v2"
# DEFAULT_DB_PATH = Path.home() / ".cache" / "repo_rag"


# class RepoRAG:
#     def __init__(self, db_path: Path, model_name: str = DEFAULT_MODEL) -> None:
#         self.db_path = db_path
#         self.db_path.mkdir(parents=True, exist_ok=True)
        
#         with console.status(f"[bold green]Loading embedding model: {model_name}..."):
#             self.model = SentenceTransformer(model_name)
        
#         self.client = chromadb.PersistentClient(
#             path=str(db_path),
#             settings=Settings(anonymized_telemetry=False)
#         )
        
#     def _get_or_create_collection(self, repo_path: Path) -> chromadb.Collection:
#         collection_name = f"repo_{repo_path.name}".replace("-", "_").replace(".", "_")
#         return self.client.get_or_create_collection(
#             name=collection_name,
#             metadata={"repo_path": str(repo_path)}
#         )
    
#     def _chunk_file_content(self, content: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
#         lines = content.split("\n")
#         chunks: list[str] = []
#         current_chunk: list[str] = []
#         current_size = 0
        
#         for line in lines:
#             line_size = len(line)
#             if current_size + line_size > chunk_size and current_chunk:
#                 chunks.append("\n".join(current_chunk))
#                 overlap_lines = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
#                 current_chunk = overlap_lines
#                 current_size = sum(len(line_text) for line_text in current_chunk)
            
#             current_chunk.append(line)
#             current_size += line_size
        
#         if current_chunk:
#             chunks.append("\n".join(current_chunk))
        
#         return chunks if chunks else [content]
    
#     def index_repo(self, repo_path: Path, extensions: list[str], max_file_size_kb: int = 500) -> None:
#         collection = self._get_or_create_collection(repo_path)
        
#         files_to_index: list[Path] = []
#         for ext in extensions:
#             files_to_index.extend(repo_path.rglob(f"*{ext}"))
        
#         files_to_index = [
#             f for f in files_to_index 
#             if not any(part.startswith('.') for part in f.relative_to(repo_path).parts[:-1])
#             and f.stat().st_size < max_file_size_kb * 1024
#         ]
        
#         console.print(f"[bold cyan]Found {len(files_to_index)} files to index")
        
#         with Progress(
#             SpinnerColumn(),
#             TextColumn("[progress.description]{task.description}"),
#             console=console
#         ) as progress:
#             task = progress.add_task("Indexing files...", total=len(files_to_index))
            
#             for file_path in files_to_index:
#                 try:
#                     content = file_path.read_text(encoding="utf-8", errors="ignore")
#                     rel_path = str(file_path.relative_to(repo_path))
                    
#                     chunks = self._chunk_file_content(content)
                    
#                     for i, chunk in enumerate(chunks):
#                         doc_id = f"{rel_path}::chunk_{i}"
#                         embedding = self.model.encode(chunk).tolist()
                        
#                         collection.upsert(
#                             ids=[doc_id],
#                             embeddings=[embedding],
#                             documents=[chunk],
#                             metadatas=[{
#                                 "file_path": rel_path,
#                                 "chunk_index": i,
#                                 "total_chunks": len(chunks),
#                                 "extension": file_path.suffix
#                             }]
#                         )
                    
#                 except Exception as e:
#                     console.print(f"[yellow]Warning: Failed to index {file_path}: {e}")
                
#                 progress.advance(task)
        
#         console.print("[bold green]✓ Indexing complete!")
    
#     def search(self, repo_path: Path, query: str, n_results: int = 20) -> list[dict[str, str | dict[str, str | int]]]:
#         collection = self._get_or_create_collection(repo_path)
        
#         with console.status("[bold green]Searching..."):
#             query_embedding = self.model.encode(query).tolist()
#             results = collection.query(
#                 query_embeddings=[query_embedding],
#                 n_results=n_results
#             )
        
#         if not results["ids"] or not results["ids"][0]:
#             return []
        
#         search_results: list[dict[str, str | dict[str, str | int]]] = []
#         for i, doc_id in enumerate(results["ids"][0]):
#             search_results.append({
#                 "id": doc_id,
#                 "file_path": results["metadatas"][0][i]["file_path"],
#                 "content": results["documents"][0][i],
#                 "distance": results["distances"][0][i] if results.get("distances") else 0.0,
#                 "metadata": results["metadatas"][0][i]
#             })
        
#         return search_results
    
#     def delete_index(self, repo_path: Path) -> None:
#         collection_name = f"repo_{repo_path.name}".replace("-", "_").replace(".", "_")
#         try:
#             self.client.delete_collection(name=collection_name)
#             console.print(f"[bold green]✓ Deleted index for {repo_path.name}")
#         except Exception as e:
#             console.print(f"[bold red]Error deleting index: {e}")


# @app.command()
# def index(
#     repo_path: Annotated[Path, typer.Argument(help="Path to repository to index")] = Path.cwd(),
#     extensions: Annotated[str, typer.Option("--ext", "-e", help="Comma-separated list of extensions")] = ",".join(DEFAULT_EXTENSIONS),
#     model: Annotated[str, typer.Option("--model", "-m", help="Sentence transformer model name")] = DEFAULT_MODEL,
#     db_path: Annotated[Path, typer.Option("--db", help="Database path")] = DEFAULT_DB_PATH,
#     max_size_kb: Annotated[int, typer.Option("--max-size", help="Max file size in KB")] = 500,
# ) -> None:
#     repo_path = repo_path.resolve()
    
#     if not repo_path.exists():
#         console.print(f"[bold red]Error: Repository path does not exist: {repo_path}")
#         raise typer.Exit(1)
    
#     ext_list = [ext.strip() if ext.startswith(".") else f".{ext.strip()}" for ext in extensions.split(",")]
    
#     console.print(f"[bold cyan]Repository:[/] {repo_path}")
#     console.print(f"[bold cyan]Extensions:[/] {', '.join(ext_list)}")
#     console.print(f"[bold cyan]Model:[/] {model}")
#     console.print(f"[bold cyan]Database:[/] {db_path}")
#     console.print()
    
#     rag = RepoRAG(db_path, model)
#     rag.index_repo(repo_path, ext_list, max_size_kb)


# @app.command()
# def search(
#     query: Annotated[str, typer.Argument(help="Search query")],
#     repo_path: Annotated[Path, typer.Option("--repo", "-r", help="Path to repository")] = Path.cwd(),
#     n_results: Annotated[int, typer.Option("--num", "-n", help="Number of results")] = 20,
#     model: Annotated[str, typer.Option("--model", "-m", help="Sentence transformer model name")] = DEFAULT_MODEL,
#     db_path: Annotated[Path, typer.Option("--db", help="Database path")] = DEFAULT_DB_PATH,
#     use_fzf: Annotated[bool, typer.Option("--fzf", help="Use fzf for interactive selection")] = True,
#     show_content: Annotated[bool, typer.Option("--content", "-c", help="Show content snippets")] = True,
# ) -> None:
#     repo_path = repo_path.resolve()
    
#     if not repo_path.exists():
#         console.print(f"[bold red]Error: Repository path does not exist: {repo_path}")
#         raise typer.Exit(1)
    
#     rag = RepoRAG(db_path, model)
#     results = rag.search(repo_path, query, n_results)
    
#     if not results:
#         console.print("[yellow]No results found")
#         raise typer.Exit(0)
    
#     if use_fzf:
#         _search_with_fzf(results, repo_path, show_content)
#     else:
#         _display_results(results, show_content)


# def _display_results(results: list[dict[str, str | dict[str, str | int]]], show_content: bool) -> None:
#     table = Table(title="Search Results", show_header=True, header_style="bold magenta")
#     table.add_column("#", style="cyan", width=4)
#     table.add_column("File", style="green")
#     table.add_column("Chunk", style="yellow", width=8)
#     table.add_column("Score", style="blue", width=8)
#     if show_content:
#         table.add_column("Content Preview", style="white", width=60)
    
#     for i, result in enumerate(results, 1):
#         file_path = str(result["file_path"])
#         metadata = result["metadata"]
#         chunk_info = f"{int(metadata['chunk_index']) + 1}/{int(metadata['total_chunks'])}"
#         score = f"{float(result['distance']):.3f}"
        
#         row = [str(i), file_path, chunk_info, score]
        
#         if show_content:
#             content = str(result["content"])
#             preview = content[:200].replace("\n", " ") + ("..." if len(content) > 200 else "")
#             row.append(preview)
        
#         table.add_row(*row)
    
#     console.print(table)


# def _search_with_fzf(results: list[dict[str, str | dict[str, str | int]]], repo_path: Path, show_content: bool) -> None:
#     try:
#         fzf_input_lines: list[str] = []
#         for i, result in enumerate(results, 1):
#             file_path = str(result["file_path"])
#             metadata = result["metadata"]
#             chunk_info = f"{int(metadata['chunk_index']) + 1}/{int(metadata['total_chunks'])}"
#             score = f"{float(result['distance']):.3f}"
            
#             if show_content:
#                 content = str(result["content"]).replace("\n", " ")[:100]
#                 line = f"{i:3d} │ {score:6s} │ {chunk_info:5s} │ {file_path:60s} │ {content}"
#             else:
#                 line = f"{i:3d} │ {score:6s} │ {chunk_info:5s} │ {file_path}"
            
#             fzf_input_lines.append(line)
        
#         fzf_input = "\n".join(fzf_input_lines)
        
#         result = subprocess.run(
#             ["fzf", "--ansi", "--multi", "--reverse", "--header=Select files to open (TAB for multi-select)"],
#             input=fzf_input.encode(),
#             capture_output=True
#         )
        
#         if result.returncode != 0:
#             console.print("[yellow]Selection cancelled")
#             return
        
#         selected_lines = result.stdout.decode().strip().split("\n")
        
#         for line in selected_lines:
#             if not line:
#                 continue
            
#             parts = line.split("│")
#             if len(parts) < 4:
#                 continue
            
#             file_path_str = parts[3].strip().split()[0]
            
#             idx = int(parts[0].strip()) - 1
#             if idx < len(results):
#                 content = str(results[idx]["content"])
                
#                 console.print(f"\n[bold green]File:[/] {file_path_str}")
#                 console.print("[bold cyan]Content:[/]")
                
#                 syntax = Syntax(content, "python", theme="monokai", line_numbers=True)
#                 console.print(syntax)
#                 console.print("\n" + "─" * 80 + "\n")
    
#     except FileNotFoundError:
#         console.print("[bold red]Error: fzf not found. Install fzf or use --no-fzf flag")
#         _display_results(results, show_content)


# @app.command()
# def delete(
#     repo_path: Annotated[Path, typer.Argument(help="Path to repository")] = Path.cwd(),
#     db_path: Annotated[Path, typer.Option("--db", help="Database path")] = DEFAULT_DB_PATH,
#     model: Annotated[str, typer.Option("--model", "-m", help="Sentence transformer model name")] = DEFAULT_MODEL,
# ) -> None:
#     repo_path = repo_path.resolve()
#     rag = RepoRAG(db_path, model)
#     rag.delete_index(repo_path)


# @app.command()
# def info() -> None:
#     console.print("[bold cyan]Repo RAG - Semantic Code Search[/]\n")
    
#     info_table = Table(show_header=False, box=None)
#     info_table.add_column("Key", style="cyan")
#     info_table.add_column("Value", style="white")
    
#     info_table.add_row("Embedding Model", DEFAULT_MODEL)
#     info_table.add_row("Vector Store", "ChromaDB (embedded)")
#     info_table.add_row("Default Extensions", ", ".join(DEFAULT_EXTENSIONS))
#     info_table.add_row("Database Path", str(DEFAULT_DB_PATH))
    
#     console.print(info_table)
    
#     console.print("\n[bold green]Quick Start:[/]")
#     console.print("1. Index your repo:     [yellow]repo-rag index[/]")
#     console.print("2. Search semantically: [yellow]repo-rag search 'your query'[/]")
#     console.print("3. Delete index:        [yellow]repo-rag delete[/]")


# if __name__ == "__main__":
#     app()
