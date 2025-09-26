
import typer

def hello(name: str):
    print(f"Hello, {name}!")

def main():
    typer.run(hello)
