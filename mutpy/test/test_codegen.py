from mutpy import codegen

def test_remove_extra_lines():
    source = """
Hello, world!

This is a test.

    Spaces before text
"""
    
    result = codegen.remove_extra_lines(source)

    expected = """Hello, world!
This is a test.
    Spaces before text"""

    assert result == expected
