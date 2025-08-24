import typer

app = typer.Typer()

@app.command()
def hello(name: str):
    """
    Says hello.
    """
    print(f"Hello {name}")

@app.command()
def goodbye(name: str):
    """
    Says goodbye.
    """
    print(f"Goodbye {name}")

if __name__ == "__main__":
    app()
