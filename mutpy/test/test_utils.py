import ast
import os
import pytest
import shutil
import sys
import tempfile
import types
import unittest

from mutpy import utils, operators

class ModulesLoaderTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix='mutpytmp-') + '/'
        os.makedirs(cls.tmp + 'a/b/c')
        open(cls.tmp + 'a/__init__.py', 'w').close()
        open(cls.tmp + 'a/b/__init__.py', 'w').close()
        open(cls.tmp + 'a/b/c/__init__.py', 'w').close()
        with open(cls.tmp + 'a/b/c/sample.py', 'w') as f:
            f.write('class X:\n\tdef f():\n\t\tpass')
        with open(cls.tmp + 'a/b/c/sample_test.py', 'w') as f:
            f.write('from a.b.c import sample')

    def assert_module(self, module_object, module_name, module_path, attrs):
        self.assertIsInstance(module_object, types.ModuleType)
        for attr in attrs:
            self.assertTrue(hasattr(module_object, attr))
        self.assertMultiLineEqual(
            os.path.abspath(module_object.__file__),
            os.path.abspath(ModulesLoaderTest.tmp + module_path),
        )
        self.assertMultiLineEqual(os.path.abspath(module_object.__name__), os.path.abspath(module_name))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def setUp(self):
        self.loader = utils.ModulesLoader(None, ModulesLoaderTest.tmp)

    def test_load_file(self):
        module, to_mutate = self.loader.load_single('a/b/c/sample.py')[0]

        self.assert_module(module, 'sample', 'a/b/c/sample.py', ['X'])
        self.assertIsNone(to_mutate)

    def test_load_module(self):
        module, to_mutate = self.loader.load_single('a.b.c.sample')[0]

        self.assert_module(module, 'a.b.c.sample', 'a/b/c/sample.py', ['X'])
        self.assertIsNone(to_mutate)

    def test_target_class(self):
        module, to_mutate = self.loader.load_single('a.b.c.sample.X')[0]

        self.assert_module(module, 'a.b.c.sample', 'a/b/c/sample.py', ['X'])
        self.assertMultiLineEqual(to_mutate, 'X')

    def test_target_method(self):
        module, to_mutate = self.loader.load_single('a.b.c.sample.X.f')[0]

        self.assert_module(module, 'a.b.c.sample', 'a/b/c/sample.py', ['X'])
        self.assertMultiLineEqual(to_mutate, 'X.f')

    def test_bad_target_class(self):
        self.assertRaises(utils.ModulesLoaderException, lambda: self.loader.load_single('a.b.c.sample.Y'))

    def test_bad_target_method(self):
        self.assertRaises(utils.ModulesLoaderException, lambda: self.loader.load_single('a.b.c.sample.X.g'))

    def test_bad_module(self):
        self.assertRaises(utils.ModulesLoaderException, lambda: self.loader.load_single('a.b.c.example'))

    def test_load_package(self):
        target, test = self.loader.load_single('a')
        self.assert_module(target[0], 'a.b.c.sample', 'a/b/c/sample.py', [])
        self.assert_module(test[0], 'a.b.c.sample_test', 'a/b/c/sample_test.py', [])


class MockTimer():

    def stop(self):
        return 1


class MockTimeRegister(utils.TimeRegister):
    timer_class = MockTimer


class TimeRegisterTest(unittest.TestCase):

    def setUp(self):
        MockTimeRegister.clean()

    def test_normal_function(self):
        @MockTimeRegister
        def foo():
            pass

        foo()

        self.assertEqual(MockTimeRegister.executions['foo'], 1)

    def test_recursion(self):
        @MockTimeRegister
        def foo(x):
            if x != 0:
                foo(x-1)

        foo(10)

        self.assertEqual(MockTimeRegister.executions['foo'], 1)

    def test_function_with_yield(self):
        @MockTimeRegister
        def foo():
            for i in [1, 2, 3]:
                yield i

        for _ in foo():
            pass

        self.assertEqual(MockTimeRegister.executions['foo'], 1)


class GetByPythonVersionTest(unittest.TestCase):

    class A:
        __python_version__ = (3, 1)

    class B:
        __python_version__ = (3, 2)

    def test_empty_classes(self):
        with self.assertRaises(NotImplementedError):
            utils.get_by_python_version(classes=[])

    def test_no_proper_class(self):
        with self.assertRaises(NotImplementedError):
            utils.get_by_python_version(classes=[self.A, self.B], python_version=(3, 0))

    def test_get_proper_class(self):
        cls = utils.get_by_python_version(classes=[self.A, self.B], python_version=(3, 1))

        self.assertEqual(cls, self.A)

    def test_get_lower_class(self):
        cls = utils.get_by_python_version(classes=[self.A, self.B], python_version=(3, 3))

        self.assertEqual(cls, self.B)


class SortOperatorsTest(unittest.TestCase):

    def test_sort_operators(self):

        class A(operators.MutationOperator):
            pass

        class Z(operators.MutationOperator):
            pass

        sorted_operators = utils.sort_operators([Z, A])

        self.assertEqual(sorted_operators[0], A)
        self.assertEqual(sorted_operators[1], Z)

def test_f_should_remove_intendation():
    input_text = """
    def f():
        pass
    """    
    result = utils.f(input_text)

    expected = "def f():\n    pass"

    assert result == expected

def test_f_should_not_remove_intendation_if_there_is_none():
    input_text = """
First line
Second line
    """    
    result = utils.f(input_text)

    expected = "First line\nSecond line"

    assert result == expected

def test_f_should_handle_empty_string():
    input_text = """"""    
    result = utils.f(input_text)

    expected = ""

    assert result == expected

def test_f_should_handle_one_newline_character():
    input_text = """\n"""
    result = utils.f(input_text)

    # first line should be stripped
    expected = ""

    assert result == expected

def test_f_should_handle_two_newline_characters():
    input_text = """\n\n"""
    result = utils.f(input_text)

    # first and last line should be stripped
    expected = ""

    assert result == expected

def test_f_should_handle_three_newline_characters():
    input_text = """\n\n\n"""
    result = utils.f(input_text)

    # first and last line should be stripped
    expected = "\n"

    assert result == expected

class InjectImporterTest(unittest.TestCase):

    def test_inject(self):
        target_module_content = utils.f("""
        def x():
            import source
            return source
        """)
        target_module = types.ModuleType('target')
        source_module_before = types.ModuleType('source')
        source_module_before.__file__ = 'source.py'
        source_module_after = types.ModuleType('source')
        sys.modules['source'] = source_module_before
        importer = utils.InjectImporter(source_module_after)

        eval(compile(target_module_content, 'target.py', 'exec'), target_module.__dict__)
        importer.install()

        source_module = target_module.x()
        self.assertEqual(source_module, source_module_after)
        self.assertEqual(source_module.__loader__, importer)

        del sys.modules['source']
        importer.uninstall()

SAMPLE_CODE_WITH_DOCSTRINGS = utils.f(
"""
\"\"\"This is a module docstring.\"\"\"
class MyClass:
    \"\"\"This is a class docstring.\"\"\"
    def my_function():
        \"\"\"This is a function docstring.\"\"\"
        pass
    """)

def test_is_docstring_should_detect_docstring_correctly():
    """Tests that is_docstring can detect docstrings correctly if using utils.create_ast()."""
    # utils.create_ast() sets parents allowing is_docstring to work correctly
    module_node = utils.create_ast(SAMPLE_CODE_WITH_DOCSTRINGS)
    
    module_docstring = module_node.body[0].value
    class_node = module_node.body[1]
    class_docstring = class_node.body[0].value
    function_node = class_node.body[1]
    function_docstring = function_node.body[0].value

    assert utils.is_docstring(module_docstring)
    assert utils.is_docstring(class_docstring)
    assert utils.is_docstring(function_docstring)

    assert not utils.is_docstring(class_node)
    assert not utils.is_docstring(function_node)

def test_is_docstring_should_raise_error_if_there_are_no_grandparents():
    """Tests that is_docstring does raise exception when using ast.parse()."""
    # ast.parse() does not set parents, so is_docstring() should raise an exception
    module_node = ast.parse(SAMPLE_CODE_WITH_DOCSTRINGS)
    
    module_docstring = module_node.body[0].value
    
    with pytest.raises(utils.NoGrandparentError):
        utils.is_docstring(module_docstring)

@pytest.mark.skipif(sys.version_info[:2] < (3,9), reason="requires python3.9")
def test_create_ast_creates_node_with_end_linenos():
    """Tests that create_ast() creates nodes with end_lineno filled in."""
    module_node = utils.create_ast(SAMPLE_CODE_WITH_DOCSTRINGS)

    module_docstring = module_node.body[0].value
    class_node = module_node.body[1]
    class_docstring = class_node.body[0].value
    function_node = class_node.body[1]
    function_docstring = function_node.body[0].value

    assert module_docstring.lineno == 1
    assert module_docstring.end_lineno == 1
    assert class_node.lineno == 2
    assert class_node.end_lineno == 6
    assert class_docstring.lineno == 3
    assert function_node.lineno == 4
    assert function_node.end_lineno == 6
    assert function_docstring.lineno == 5