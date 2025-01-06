from typing import Annotated
import os
import zlib
from pathlib import Path

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


@app.command()
def cat_file(
    blob_hash: Annotated[str, typer.Argument()],
    pretty: Annotated[bool, typer.Option("-p")] = True,
):
    blob_path = Path(f".git/objects/{blob_hash[:2]}/{blob_hash[2:]}")
    with open(blob_path, "br") as f:
        blob = zlib.decompress(f.read())
        _, content = blob.split(b"\x00")

    print(content.decode(), end="")
