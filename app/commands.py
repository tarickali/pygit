from typing import Annotated
import os
import zlib
import hashlib
import pathlib

import typer

__all__ = ["app"]

app = typer.Typer()


@app.command()
def init() -> None:
    os.makedirs(".git", exist_ok=True)
    os.makedirs(".git/objects", exist_ok=True)
    os.makedirs(".git/refs", exist_ok=True)

    with open(".git/HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")

    print("Initialized git directory")


@app.command()
def cat_file(
    blob_hash: Annotated[str, typer.Argument()],
    exists: Annotated[bool, typer.Option("-e")] = None,
    pretty: Annotated[bool, typer.Option("-p")] = None,
) -> None:

    if exists is None and pretty is None:
        print("Require one of the following arguments: -e or -p")
        typer.Abort()
        return
    if exists is not None and pretty is not None:
        print("Options -e and -p cannot be used together")
        typer.Abort()
        return

    blob_path = pathlib.Path(f".git/objects/{blob_hash[:2]}/{blob_hash[2:]}")

    if not os.path.exists(blob_path):
        print(f"Blob with hash:{blob_hash} does not exist")
        typer.Abort()
        return

    with open(blob_path, "br") as file:
        blob = zlib.decompress(file.read())
        _, content = blob.split(b"\x00")

    if pretty is not None:
        print(content.decode(), end="")


@app.command()
def hash_object(
    file_path: Annotated[str, typer.Argument()],
    write: Annotated[bool, typer.Option("-w")] = False,
) -> None:
    with open(pathlib.Path(file_path), "r") as file:
        content = file.read()

    blob = f"blob {len(content)}\0{content}".encode()
    blob_hash = hashlib.sha1(blob).hexdigest()

    blob_directory = pathlib.Path(f".git/objects/{blob_hash[:2]}")
    blob_file_path = blob_directory / pathlib.Path(blob_hash[2:])

    if write:
        os.makedirs(blob_directory, exist_ok=True)
        with open(blob_file_path, "wb+") as file:
            file.write(zlib.compress(blob))

    print(blob_hash)
