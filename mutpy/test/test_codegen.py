"""Unit tests for codegen.py."""

from mutpy import codegen


def test_add_line_numbers() -> None:
    source = """Hello, world!

This is a test.

    Spaces before text"""

    result = codegen.add_line_numbers(source)

    expected = """ 1: Hello, world!
 2: 
 3: This is a test.
 4: 
 5:     Spaces before text"""

    assert result == expected


def test_remove_extra_lines() -> None:
    source = """
Hello, world!

This is a test.

    Spaces before text"""

    result = codegen.remove_extra_lines(source)

    expected = """Hello, world!
This is a test.
    Spaces before text"""

    assert result == expected
