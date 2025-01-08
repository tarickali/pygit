import os
from pathlib import Path
import hashlib
from datetime import datetime
import zlib

__all__ = ["create_blob", "create_tree"]


def create_blob(path: Path, write: bool = False) -> str:
    with open(path, "r") as file:
        content = file.read()

    blob = f"blob {len(content)}\0{content}".encode()
    blob_hash = hashlib.sha1(blob).hexdigest()

    blob_directory = Path(f".git/objects/{blob_hash[:2]}")
    blob_path = blob_directory / Path(blob_hash[2:])

    if write and not os.path.exists(blob_path):
        os.makedirs(blob_directory, exist_ok=True)
        with open(blob_path, "bw") as file:
            file.write(zlib.compress(blob))
        blob_path.chmod(0o444)

    return blob_hash


def create_tree(path: Path) -> str:
    if os.path.isfile(path):
        return create_blob(path, write=True)

    entries = sorted(
        os.listdir(path),
        key=lambda entry: (
            entry if os.path.isfile(os.path.join(path, entry)) else f"{entry}/"
        ),
    )

    tree_entries = b""
    for entry in entries:
        if entry == ".git":
            continue

        fullpath = path / Path(entry)

        mode = 40000  # directory
        if os.path.isfile(fullpath):  # regular file
            mode = 100644
            if os.access(fullpath, os.X_OK):  # executable file
                mode = 100755
            elif os.path.islink(fullpath):  # symbolic link
                mode = 120000

        entry_hash = int.to_bytes(int(create_tree(fullpath), base=16), length=20)

        tree_entries += f"{mode} {entry}\0".encode() + entry_hash

    tree = f"tree {len(tree_entries)}\0".encode() + tree_entries
    tree_hash = hashlib.sha1(tree).hexdigest()

    tree_directory = Path(f".git/objects/{tree_hash[:2]}")
    tree_path = tree_directory / Path(tree_hash[2:])

    if not os.path.exists(tree_path):
        os.makedirs(tree_directory, exist_ok=True)
        with open(tree_path, "wb") as f:
            f.write(zlib.compress(tree))
        tree_path.chmod(0o444)

    return tree_hash


def create_commit(
    tree_hash: str, messages: list[str], parents: list[str] = None
) -> str:
    author_name = committer_name = "tarickali"
    author_email = committer_email = "tarickali97@gmail.com"
    author_date_seconds = committer_date_seconds = datetime.now().timestamp()
    author_date_timezone = committer_date_timezone = (
        datetime.now().astimezone().strftime("%z")
    )

    content = f"tree {tree_hash}\n"
    if parents is not None:
        content += "\n".join(f"parent {parent}" for parent in parents) + "\n"
    content += f"author {author_name} <{author_email}> {author_date_seconds} {author_date_timezone}\n"
    content += f"committer {committer_name} <{committer_email}> {committer_date_seconds} {committer_date_timezone}\n"
    content += "\n" + "\n\n".join(messages) + "\n"

    commit = f"commit {len(content)}\0{content}".encode()
    commit_hash = hashlib.sha1(commit).hexdigest()

    commit_directory = Path(f".git/objects/{commit_hash[:2]}")
    commit_path = commit_directory / Path(commit_hash[2:])

    if not os.path.exists(commit_path):
        os.makedirs(commit_directory, exist_ok=True)
        with open(commit_path, "bw") as f:
            f.write(zlib.compress(commit))
        commit_path.chmod(0o444)

    return commit_hash
