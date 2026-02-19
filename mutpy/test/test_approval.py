from mutpy import commandline
from approvaltests.approvals import verify
from approvaltests.namer import NamerFactory

import pytest
import re
import sys

# --- Tests ---

@pytest.mark.slow
def test_approval(capsys, monkeypatch):
    """
    Validates mutation testing example against platform-specific approved files.
    """
    custom_args = [
        "mut.py",
        "--target", "example/simple.py",
        "--unit-test", "example/test/simple_good_test.py",
    ]

    monkeypatch.setattr(sys, "argv", custom_args)

    try:
        commandline.main(sys.argv)
    except SystemExit:
        # commandline.main() calls sys.exit() with the number of survivors
        pass
    
    output = capsys.readouterr().out
    
    # This appends the OS name to the approved file (e.g., .win32.approved.txt)
    options = NamerFactory.with_parameters(sys.platform)
    verify(_normalize(output), options=options)

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
