from mutpy import commandline
from approvaltests.approvals import verify

import pytest
import re
import sys

# --- Tests ---

custom_args = [
    "mut.py",
    "--target", "example/simple.py",
    "--unit-test", "example/test/simple_good_test.py",
    "--debug",
    "--show-mutants",
]

sys.argv = custom_args

@pytest.mark.slow
def test_approval(capsys):
    commandline.main(sys.argv)
    output = capsys.readouterr().out
    verify(_normalize(output))

def test_normalize():
    assert _normalize("[5.00672 s]") == "<TIMESTAMP>"
    assert _normalize("[0.00001 s]") == "<TIMESTAMP>"
    assert _normalize("[29.96068 s]") == "<TIMESTAMP>"
    assert _normalize("no timing here") == "no timing here"

# --- Helper Functions ---

def _normalize(text: str) -> str:
    """Helper function to replace timestamps with <TIMESTAMP>."""
    TIME_REGEX = r"\[\d+(?:\.\d+)?\s*s\]"
    return re.sub(TIME_REGEX, "<TIMESTAMP>", text)
