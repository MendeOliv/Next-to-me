# tests/test_utils.py
from utils import git_hash

def test_git_hash():
    """
    Tests that the git_hash function returns a string.
    """
    h = git_hash()
    assert isinstance(h, str)
    assert len(h) > 0
