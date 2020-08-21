import logging
import unittest

from step_manager._Expected import Expected
from unittest.mock import MagicMock, Mock

test_name = "Forrest"
test_value = "Gump"


class TestExpected(unittest.TestCase):

    def setUp(self) -> None:
        self.owner = Mock()
        self.owner.log = MagicMock()

    def test_run_success(self):
        test_method = MagicMock(return_value=True)
        expected = Expected(self.owner, test_method, name=test_name, value=test_value)
        result = expected.run()
        test_method.assert_called_once_with(name=test_name, value=test_value)
        self.assertTrue(result[0])
        self.assertEqual("", result[1])

    def test_run_failure(self):
        error_message = "Something happened"
        test_method = MagicMock(return_value=(False, error_message))
        expected = Expected(self.owner, test_method, name=test_name, value=test_value)
        result = expected.run()
        test_method.assert_called_once_with(name=test_name, value=test_value)
        self.assertFalse(result[0])
        self.assertEqual(error_message, result[1])

    def test_run_failure_without_message(self):
        test_method = MagicMock(return_value=False)
        expected = Expected(self.owner, test_method, name=test_name, value=test_value)
        result = expected.run()
        test_method.assert_called_once_with(name=test_name, value=test_value)
        self.assertFalse(result[0])
        self.assertEqual("No message provided", result[1])

    def test_success_should_return_with_custom_value(self):
        value = 15
        test_method = MagicMock(return_value=value)
        expected = Expected(self.owner, test_method, name=test_name, value=test_value, should_return=value)
        result = expected.run()
        test_method.assert_called_once_with(name=test_name, value=test_value)
        self.assertTrue(result[0])

    def test_failure_should_return_with_custom_value(self):
        value = 15
        test_method = MagicMock(return_value=17)
        expected = Expected(self.owner, test_method, name=test_name, value=test_value, should_return=value)
        result = expected.run()
        test_method.assert_called_once_with(name=test_name, value=test_value)
        self.assertFalse(result[0])

    def test_disabled_should_return(self):
        test_method = MagicMock(return_value=False)
        expected = Expected(self.owner, test_method, name=test_name, value=test_value, should_return=False)
        result = expected.run()
        test_method.assert_called_once_with(name=test_name, value=test_value)

    def test_is_alert(self):
        test_method = MagicMock(return_value=True)
        expected = Expected(self.owner, test_method, name=test_name, value=test_value, is_alert=True)
        self.assertTrue(expected.is_alert)


if __name__ == '__main__':
    unittest.main()
