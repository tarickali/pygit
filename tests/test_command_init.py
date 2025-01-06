import os
import sys


def test_command_init():
    test_dir = ".test_dir/"

    assert os.path.exists(test_dir + ".git")
    assert os.path.exists(test_dir + ".git/objects")
    assert os.path.exists(test_dir + ".git/refs")
    assert os.path.exists(test_dir + ".git/HEAD")

    with open(test_dir + ".git/HEAD") as f:
        content = f.read()
        assert content == "ref: refs/heads/main\n"
