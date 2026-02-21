import pytest
import sys

from mutpy import mut


def test_main_version_exits_zero(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["mutpy", "--version"])
    with pytest.raises(SystemExit) as exc:
        mut.main()
    assert exc.value.code == 0
