import unittest

from mutpy import coverage, utils
from mutpy.test_runners.unittest_runner import UnittestCoverageResult


class MarkerNodeTransformerTest(unittest.TestCase):
    def test_visit(self):
        node = utils.create_ast('x = y\ny = x')
        coverage.MarkerNodeTransformer().visit(node)

        y_load_node = node.body[0].value.ctx
        x_load_node = node.body[1].value.ctx

        self.assertTrue(y_load_node.marker < x_load_node.marker)


class CoverageInjectorTest(unittest.TestCase):
    def setUp(self):
        self.coverage_injector = coverage.CoverageInjector()

    def assert_covered(self, nodes):
        for node in nodes:
            self.assertTrue(self.coverage_injector.is_covered(node))

    def assert_not_covered(self, nodes):
        for node in nodes:
            self.assertFalse(self.coverage_injector.is_covered(node))

    def test_covered_node(self):
        node = utils.create_ast('x = 1\nif False:\n\ty = 2')

        self.coverage_injector.inject(node)

        assign_node = node.body[0]
        constant_node = node.body[0].targets[0]
        self.assert_covered([assign_node, constant_node])

    def test_line_numbers_after_injection(self):
        node = utils.create_ast(utils.f("""
from mutpy.utils import notmutate


class Base:
    X = 1

    def foo(self):
        return 1

    def bar(self):
        self.x = 1
"""
        ))

        self.coverage_injector.inject(node)

        self.assertEqual(node.body[0].lineno, 1)  # Import statement at line 1
        self.assertEqual(node.body[1].lineno, 4)  # Class definition starts at line 4
        self.assertEqual(node.body[1].body[0].lineno, 5)  # Assignment X = 1 at line 5
        self.assertEqual(node.body[1].body[1].lineno, 7)  # Method def foo(self): at line 7
        self.assertEqual(node.body[1].body[1].body[0].lineno, 8) # return 1: at line 8
        self.assertEqual(node.body[1].body[2].lineno, 10)  # Method def bar(self): at line 10
        self.assertEqual(node.body[1].body[2].body[0].lineno, 11)  # self.x = 1 at line 11    

    def test_not_covered_node(self):
        node = utils.create_ast('if False:\n\ty = 2')

        self.coverage_injector.inject(node)

        assign_node = node.body[0].body[0]
        constant_node = node.body[0].body[0].targets[0]
        self.assert_not_covered([assign_node, constant_node])

    def test_result(self):
        node = utils.create_ast('x = 1')

        self.coverage_injector.inject(node)

        self.assertEqual(self.coverage_injector.get_result(), (5, 5))

    def test_future_statement_coverage(self):
        node = utils.create_ast('from __future__ import print_function')

        self.coverage_injector.inject(node)

        import_node = node.body[0]
        self.assert_not_covered([import_node])

    def test_docstring_coverage(self):
        node = utils.create_ast('"""doc"""')

        self.coverage_injector.inject(node)

        docstring_node = node.body[0]
        self.assert_covered([docstring_node])

    def test_if_coverage(self):
        node = utils.create_ast(utils.f("""
        if False:
            pass
        elif True:
            pass
        else:
            pass
        """))

        self.coverage_injector.inject(node)

        if_node = node.body[0]
        first_if_test_node = if_node.test
        first_if_body_el = if_node.body[0]
        second_if_node = if_node.orelse[0]
        second_if_test_node = second_if_node.test
        second_if_body_el = second_if_node.body[0]
        else_body_el = second_if_node.orelse[0]

        self.assert_covered([first_if_test_node, second_if_test_node, second_if_body_el])
        self.assert_not_covered([first_if_body_el, else_body_el])

    def test_while__coverage(self):
        node = utils.create_ast(utils.f("""
        while False:
            pass
        else:
            pass
        """))

        self.coverage_injector.inject(node)

        while_node = node.body[0]
        while_test_node = while_node.test
        while_body_el = while_node.body[0]
        while_else_body_el = while_node.orelse[0]

        self.assert_covered([while_test_node, while_else_body_el])
        self.assert_not_covered([while_body_el])

    def test_func_def_coverage(self):
        node = utils.create_ast(utils.f("""
        def foo(x):
            pass
        """))

        self.coverage_injector.inject(node)

        func_node = node.body[0]
        func_body_el = func_node.body[0]
        arg_node = func_node.args.args[0]

        self.assert_covered([func_node, arg_node])
        self.assert_not_covered([func_body_el])

    def test_class_def_coverage(self):
        node = utils.create_ast(utils.f("""
        class X(object):

            def foo(x):
                pass
        """))

        self.coverage_injector.inject(node)

        class_node = node.body[0]
        base_node = class_node.bases[0]
        func_body_el = class_node.body[0].body[0]
        self.assert_covered([class_node, base_node])
        self.assert_not_covered([func_body_el])

    def test_try_coverage(self):
        node = utils.create_ast(utils.f("""
        try:
            pass
        except:
            pass
        """))

        self.coverage_injector.inject(node)

        try_node = node.body[0]
        try_body_el = try_node.body[0]
        except_node = try_node.handlers[0]
        except_body_el = except_node.body[0]
        self.assert_covered([try_node, try_body_el])
        self.assert_not_covered([except_node, except_body_el])

    def test_except_coverage(self):
        node = utils.create_ast(utils.f("""
        try:
            raise KeyError
        except KeyError:
            pass
        """))

        self.coverage_injector.inject(node)

        try_node = node.body[0]
        try_body_el = try_node.body[0]
        except_node = try_node.handlers[0]
        except_body_el = except_node.body[0]
        self.assert_covered([try_node, try_body_el, except_node, except_body_el])

    def test_for_coverage(self):
        node = utils.create_ast(utils.f("""
        for x in []:
            pass
        else:
            pass
        """))

        self.coverage_injector.inject(node)

        for_node = node.body[0]
        for_body_el = for_node.body[0]
        else_body_el = for_node.orelse[0]
        self.assert_covered([for_node, for_node.target, for_node.iter, else_body_el])
        self.assert_not_covered([for_body_el])


class UnittestCoverageResultTest(unittest.TestCase):
    def test_run(self):
        coverage_injector = coverage.CoverageInjector()

        class A:
            def x(self):
                coverage_injector.covered_nodes.add(1)

        class ATest(unittest.TestCase):
            def test_x(self):
                A().x()

            def test_y(self):
                pass

        result = UnittestCoverageResult(coverage_injector=coverage_injector)
        suite = unittest.TestSuite()
        test_x = ATest(methodName='test_x')
        suite.addTest(test_x)
        test_y = ATest(methodName='test_y')
        suite.addTest(test_y)

        suite.run(result)

        self.assertEqual(coverage_injector.covered_nodes, {1})
        self.assertEqual(result.test_covered_nodes[repr(test_x)], {1})
        self.assertFalse(result.test_covered_nodes[repr(test_y)])

import ast
from mutpy.coverage import AbstractCoverageNodeTransformer

class TestCoverageNodeTransformer(AbstractCoverageNodeTransformer):
    @classmethod
    def get_coverable_nodes(cls):
        return {ast.Assign, ast.If, ast.FunctionDef}

class TestAbstractCoverageNodeTransformer(unittest.TestCase):
    def setUp(self):
        self.transformer = TestCoverageNodeTransformer()

    def test_inject_before_visit_for_assign(self):
        node = ast.Assign(
            targets=[ast.Name(id='x', ctx=ast.Store())],
            value=ast.Constant(value=1)
        )
        node.lineno = 1  # Set line number for the node
        node.col_offset = 0  # Set column offset

        # Apply the transformer
        transformed_nodes = self.transformer.visit(node)
        
        # Ensure that coverage node is inserted before the original node
        self.assertEqual(len(transformed_nodes), 2)  # Should be coverage node + original node
        coverage_node = transformed_nodes[0]
        self.assertIsInstance(coverage_node, ast.Expr)  # Coverage node should be an Expr (typically)
        self.assertEqual(coverage_node.lineno, node.lineno)  # Same line number as the original node
        self.assertEqual(coverage_node.col_offset, node.col_offset)

    def test_inject_inside_visit_for_function(self):
        node = ast.FunctionDef(
            name='my_function',
            args=ast.arguments(
                args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]
            ),
            body=[ast.Pass()],
            decorator_list=[],
            lineno=1,
            col_offset=0
        )

        transformed_node = self.transformer.inject_inside_visit(node)

        self.assertEqual(len(transformed_node.body), 2)  # One original Pass node + the coverage node
        coverage_node = transformed_node.body[0]
        self.assertIsInstance(coverage_node, ast.Expr)  # Coverage node should be an Expr
        self.assertEqual(coverage_node.lineno, node.lineno)  # Same line number as function
        self.assertEqual(coverage_node.col_offset, node.col_offset) # Same column offset as function
