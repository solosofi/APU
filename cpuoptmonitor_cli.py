import typer

app = typer.Typer()

@app.command()
def start():
    """
    Starts the CpuOptMonitor dashboard.
    """
    print("CLI is working!")

if __name__ == "__main__":
    app()
