"""Utility functions for code generation."""

import ast


def to_source(node: ast.AST) -> str:
    """Convert an AST node back to source code."""
    return ast.unparse(node)


def add_line_numbers(source: str) -> str:
    """Add line numbers to the source code."""
    lines = source.split("\n")
    width = len(str(len(lines))) + 1

    return "\n".join(
        "{:>{}}: {}".format(i, width, line) for i, line in enumerate(lines, start=1)
    )


def remove_extra_lines(source: str) -> str:
    """Remove extra lines from the source code."""
    parts = source.split("\n")
    result = [part for part in parts if part.strip()]
    return "\n".join(result)
