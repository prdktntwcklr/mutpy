import ast
import copy
import sys

from mutpy import utils

COVERAGE_SET_NAME = '__covered_nodes__'


class MarkerNodeTransformer(ast.NodeTransformer):

    def __init__(self):
        super().__init__()
        self.last_marker = 0

    def visit(self, node):
        node.marker = self.last_marker
        self.last_marker += 1
        return super().visit(node)


class AbstractCoverageNodeTransformer(ast.NodeTransformer):

    @classmethod
    def get_coverable_nodes(cls):
        raise NotImplementedError()

    def __init__(self):
        super().__init__()
        for node_class in self.get_coverable_nodes():
            visit_method_name = 'visit_' + node_class.__name__
            if not hasattr(self, visit_method_name):
                if node_class == ast.ExceptHandler:
                    setattr(self, visit_method_name, self.inject_inside_visit)
                else:
                    setattr(self, visit_method_name, self.inject_before_visit)

    def inject_before_visit(self, node):
        node = self.generic_visit(node)
        if self.is_future_statement(node):
            return node
        coverage_node = self.generate_coverage_node(node)
        return [coverage_node, node]

    def inject_inside_visit(self, node):
        node = self.generic_visit(node)
        coverage_node = self.generate_coverage_node(node)
        node.body.insert(0, coverage_node)
        return node

    def generate_coverage_node(self, node):
        if hasattr(node, 'body'):
            markers = self.get_markers_from_body_node(node)
        else:
            markers = self.get_included_markers(node)
        coverage_node = utils.create_ast('{}.update({})'.format(COVERAGE_SET_NAME, repr(markers))).body[0]
        coverage_node.lineno = node.lineno
        coverage_node.col_offset = node.col_offset
        if sys.version_info[:2] >= (3, 9):
            coverage_node.end_lineno = node.end_lineno
        return coverage_node

    def is_future_statement(self, node):
        return isinstance(node, ast.ImportFrom) and node.module == '__future__'

    def get_included_markers(self, node, without=None):
        markers = {n.marker for n in ast.walk(node) if hasattr(n, 'marker')}
        if without:
            for n in without:
                markers.difference_update(self.get_included_markers(n))
        return markers

    def get_markers_from_body_node(self, node):
        if isinstance(node, (ast.If, ast.While)):
            return {node.marker} | self.get_included_markers(node.test)
        elif isinstance(node, ast.For):
            return {node.marker} | self.get_included_markers(node.target) | self.get_included_markers(node.iter)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            return self.get_included_markers(node, without=node.body)
        else:
            return {node.marker}
    

class CoverageNodeTransformer(AbstractCoverageNodeTransformer):
    """
    Standard coverage transformer for Python 3.7+.
    Replaces the old 3.2 and 3.3 specific variants.
    """
    __python_version__ = (3, 7)

    @classmethod
    def get_coverable_nodes(cls):
        return {
            ast.AnnAssign,
            ast.Assert,
            ast.Assign,
            ast.AsyncFor,
            ast.AsyncFunctionDef,
            ast.AsyncWith,
            ast.AugAssign,
            ast.Break,
            ast.ClassDef,
            ast.Continue,
            ast.Delete,
            ast.ExceptHandler,
            ast.Expr,
            ast.For,
            ast.FunctionDef,
            ast.Global,
            ast.If,
            ast.Import,
            ast.ImportFrom,
            ast.Nonlocal,
            ast.Pass,
            ast.Raise,
            ast.Return,
            ast.Try,
            ast.While,
        }
    

class CoverageNodeTransformerPython310(AbstractCoverageNodeTransformer):
    """
    Coverage transformer for Python 3.10+.
    """
    __python_version__ = (3, 10)

    @classmethod
    def get_coverable_nodes(cls):
        return {
            ast.Assert,
            ast.Assign,
            ast.AsyncFor,
            ast.AsyncFunctionDef,
            ast.AsyncWith,
            ast.AugAssign,
            ast.Break,
            ast.ClassDef,
            ast.Continue,
            ast.Delete,
            ast.ExceptHandler,
            ast.Expr,
            ast.For,
            ast.FunctionDef,
            ast.Global,
            ast.If,
            ast.Import,
            ast.ImportFrom,
            ast.Match,  # new
            ast.Nonlocal,
            ast.Pass,
            ast.Raise,
            ast.Return,
            ast.Try,
            ast.While,
        }


CoverageNodeTransformer = utils.get_by_python_version([
    CoverageNodeTransformer,
    CoverageNodeTransformerPython310,
])


class CoverageInjector:

    def __init__(self):
        self.covered_nodes = set()

    def inject(self, node, module_name='coverage'):
        self.covered_nodes.clear()
        self.marker_transformer = MarkerNodeTransformer()
        marker_node = self.marker_transformer.visit(node)
        coverage_node = CoverageNodeTransformer().visit(copy.deepcopy(marker_node))
        self.covered_nodes.add(coverage_node.marker)
        with utils.StdoutManager():
            return utils.create_module(
                ast_node=coverage_node,
                module_name=module_name,
                module_dict={COVERAGE_SET_NAME: self.covered_nodes},
            )

    def is_covered(self, child_node):
        return child_node.marker in self.covered_nodes

    def get_result(self):
        return len(self.covered_nodes), self.marker_transformer.last_marker
