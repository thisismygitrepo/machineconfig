
import typer
from typing import Annotated

def func(name: str):
    print(f"Hello, {name}! from func")

def hello(*, name: Annotated[str, typer.Option(..., help="Name to greet")]):
    print(f"Hello, {name}!")

def main():
    typer.run(hello)

if __name__ == "__main__":
    # typer.run(hello)
    main()
    pass
