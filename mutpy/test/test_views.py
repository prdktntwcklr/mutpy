import pytest
import sys
import unittest

from contextlib import contextmanager
from io import StringIO
from unittest.mock import MagicMock

from mutpy import utils
from mutpy.views import QuietTextView, TextView, ViewNotifier

COLOR_RED = 'red'


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class QuietTextViewTest(unittest.TestCase):
    @staticmethod
    def get_quiet_text_view(colored_output=False):
        return QuietTextView(colored_output=colored_output)

    def test_decorate_with_color(self):
        # given
        text_view = self.get_quiet_text_view(colored_output=True)
        text = 'mutpy'
        expected_colored_text = '\x1b[31mmutpy\x1b[0m'
        # when
        colored_text = text_view.decorate(text, color=COLOR_RED)
        # then
        self.assertEqual(expected_colored_text, colored_text)


class TextViewTest(unittest.TestCase):
    SEPARATOR = '--------------------------------------------------------------------------------'
    EOL = "\n"

    @staticmethod
    def get_text_view(colored_output=False, show_mutants=False):
        return TextView(colored_output=colored_output, show_mutants=show_mutants)

    def test_print_code(self):
        # given
        text_view = self.get_text_view(show_mutants=True)
        original = utils.create_ast('x = x + 1')
        mutant = utils.create_ast('x = x - 1')
        # when
        with captured_output() as (out, err):
            text_view.print_code(mutant, original)
        # then
        output = out.getvalue().strip()
        self.assertEqual(
            self.SEPARATOR + self.EOL + '- 1: x = x + 1' + self.EOL + '+ 1: x = x - 1' + self.EOL + self.SEPARATOR,
            output
        )

def test_normalize_killer():
    assert TextView().normalize_killer("test_negate_number (simple_good_test.SimpleGoodTest.test_negate_number)") == "test_negate_number (simple_good_test.SimpleGoodTest)"
    assert TextView().normalize_killer("test_negate_number (simple_good_test.SimpleGoodTest)") == "test_negate_number (simple_good_test.SimpleGoodTest)"

def test_view_notifier_dispatches_calls():
    mock_view_1 = MagicMock()
    mock_view_2 = MagicMock()
    
    notifier = ViewNotifier([mock_view_1, mock_view_2])
    
    notifier.notify_initialize(targets=['math_lib'], tests=['test_math'])
    
    mock_view_1.initialize.assert_called_once_with(targets=['math_lib'], tests=['test_math'])
    mock_view_2.initialize.assert_called_once_with(targets=['math_lib'], tests=['test_math'])

def test_view_notifier_ignores_missing_methods():
    mock_view = MagicMock(spec=[])
    notifier = ViewNotifier([mock_view])
    
    # This should not raise an AttributeError even if the view lacks the method
    notifier.notify_something_random()

def test_view_notifier_raises_attribute_error():
    mock_view = MagicMock(spec=[])
    notifier = ViewNotifier([mock_view])
    
    with pytest.raises(AttributeError):
        # does not start with notify_ prefix, should trigger Exception
        notifier.something_else()

def test_view_notifier_add_view():
    mock_view = MagicMock()
    notifier = ViewNotifier([])
    notifier.add_view(mock_view)

    notifier.notify_initialize(targets=['math_lib'], tests=['test_math'])

    mock_view.initialize.assert_called_once_with(targets=['math_lib'], tests=['test_math'])

def test_view_notifier_del_view():
    mock_view_1 = MagicMock()
    mock_view_2 = MagicMock()
    
    notifier = ViewNotifier([mock_view_1, mock_view_2])
    notifier.del_view(mock_view_2)
    
    notifier.notify_initialize(targets=['math_lib'], tests=['test_math'])
    
    mock_view_1.initialize.assert_called_once_with(targets=['math_lib'], tests=['test_math'])

def test_quiet_text_view_time_format():
    assert QuietTextView.time_format(1.234567) == "[1.23457 s]"
    assert QuietTextView.time_format(None) == "[    -    ]"
