from typing import Annotated
import typer

import os
from pathlib import Path
import zlib

from .helpers import create_blob, create_tree, create_commit

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

    blob_path = Path(f".git/objects/{blob_hash[:2]}/{blob_hash[2:]}")

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
    file: Annotated[str, typer.Argument()],
    write: Annotated[bool, typer.Option("-w")] = False,
) -> None:
    blob_hash = create_blob(Path(file), write)
    print(blob_hash)


@app.command()
def ls_tree(
    tree_hash: Annotated[str, typer.Argument()],
    name_only: Annotated[bool, typer.Option("--name-only")] = False,
) -> None:
    tree_path = Path(f".git/objects/{tree_hash[:2]}/{tree_hash[2:]}")
    with open(tree_path, "br") as file:
        tree = zlib.decompress(file.read())

    _, tree_entries = tree.split(b"\x00", maxsplit=1)

    entries: list[bytes] = []
    i = 0
    while i < len(tree_entries):
        j = tree_entries.find(0x00, i) + 21
        entries.append(tree_entries[i:j])
        i = j

    objects: list[tuple[str, str, str, str]] = []
    for entry in entries:
        mode, rest = entry.split(b" ")
        name, content = rest.split(b"\x00", maxsplit=1)

        mode = mode.decode().zfill(6)
        name = name.decode()
        content = content.hex()
        kind = "tree" if mode == "040000" else "blob"

        objects.append((mode, kind, content, name))

    for obj in objects:
        if name_only:
            print(obj[-1])
        else:
            print(f"{obj[0]} {obj[1]} {obj[2]}\t{obj[3]}")


@app.command()
def write_tree() -> None:
    tree_hash = create_tree(Path("."))
    print(tree_hash)


@app.command()
def commit_tree(
    tree_hash: Annotated[str, typer.Argument()],
    messages: Annotated[list[str], typer.Option("-m")] = None,
    parents: Annotated[list[str], typer.Option("-p")] = None,
) -> None:
    if messages is None:
        print("No message given, aborting commit")
        typer.Abort()
        return

    commit_hash = create_commit(tree_hash, messages, parents)
    print(commit_hash)
