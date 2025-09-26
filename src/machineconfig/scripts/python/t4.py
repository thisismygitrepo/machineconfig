
import typer


def func(name: str):
    print(f"Hello, {name}! from func")

def hello(name: str):
    print(f"Hello, {name}!")

def main():
    typer.run(hello)

if __name__ == "__main__":
    # typer.run(hello)
    pass
