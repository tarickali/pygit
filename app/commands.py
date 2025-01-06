import os

import typer

__all__ = ["app"]

app = typer.Typer()


@app.command()
def init():
    os.makedirs(".git", exist_ok=True)
    os.makedirs(".git/objects", exist_ok=True)
    os.makedirs(".git/refs", exist_ok=True)

    with open(".git/HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")

    print("Initialized git directory")
