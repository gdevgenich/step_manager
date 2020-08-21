import unittest
from unittest.mock import MagicMock, Mock

from step_manager import StepManager

steps = ["Shinji", "Ryoji", "Yui", "Gendo", "Misato", "Asuka", "Rei", "Kaworu"]


class TestSm(unittest.TestCase):

    def setUp(self) -> None:
        self.sm = StepManager()
        for step_name in steps:
            self.sm.add_step(step_name)

    def test_completed(self):
        self.assertFalse(self.sm.completed)

    def test_base_duration(self):
        self.assertEqual(0.0, self.sm.get_duration())

    def test_set_duration(self):
        duration = 10
        self.sm.set_duration(10)

        self.assertEqual(duration, self.sm.get_duration())

    def test_set_and_get(self):
        value = "Ritsuko"
        self.sm.set("name", value)

        self.assertEqual(value, self.sm.get("name"))

    def test_exec_after(self):
        self.assertIsNone(self.sm.get_exec_after())

        mock = Mock()

        self.sm.set_exec_after(mock)

        self.assertEqual(mock, self.sm.get_exec_after())

    def test_has_alerts(self):
        self.assertFalse(self.sm.has_alerts())

    def test_has_warnings(self):
        self.assertFalse(self.sm.has_warnings())

    def test_add_step(self):
        step = self.sm.add_step("Hello")

        self.assertIsNotNone(step)

    def test_find_step(self):
        original = self.sm.add_step("Hello")
        find = self.sm.find_step("Hello")

        self.assertEqual(original, find)

    def test_find_step_index(self):
        step_index = 5
        index = self.sm.find_step_index(steps[step_index])

        self.assertEqual(step_index, index)

    def test_find_steps(self):
        quantity = 10
        name = "hello"
        for i in range(0, quantity):
            self.sm.add_step(name)

        steps = self.sm.find_steps(name)

        self.assertEqual(quantity, len(steps))

    def test_find_last_step_index(self):
        quantity = 10
        name = "hello"
        for i in range(0, quantity):
            self.sm.add_step(name)
        index = self.sm.find_last_step_index(name)
        expected_index = len(steps) - 1 + quantity

        self.assertEqual(expected_index, index)

    def test_remove_step(self):
        index = 3
        step_name = steps[index]

        find = self.sm.find_step(step_name)
        self.assertIsNotNone(find)

        self.sm.remove_step(step_name)

        with self.assertRaises(Exception):
            self.sm.find_step(step_name)

    def test_remove_steps_between(self):
        start = steps[1]
        stop = steps[-2]
        self.sm.remove_steps_between(start, stop)

        for step_name in steps[1:-2]:
            with self.assertRaises(Exception):
                self.sm.find_step(step_name)

    def test_remove_step_from_bottom(self):
        index = len(steps) - 1
        step_name = steps[index]

        find = self.sm.find_step(step_name)
        self.assertIsNotNone(find)

        self.sm.remove_step(step_name)

        with self.assertRaises(Exception):
            self.sm.find_step(step_name)

    def test_add_step_before(self):
        index = 3
        step_name = "Maya"
        step_name_next = steps[index]
        step_index_original = self.sm.find_step_index(step_name_next)

        self.sm.add_step_before(step_name_next, step_name)
        step_index = self.sm.find_step_index(step_name)

        self.assertEqual(step_index_original, step_index)

    def test_add_step_after(self):
        index = 4
        step_name = "Maya"
        step_name_previous = steps[index]
        step_index_original = self.sm.find_step_index(step_name_previous)

        self.sm.add_step_after(step_name_previous, step_name)
        step_index = self.sm.find_step_index(step_name)

        self.assertEqual(step_index_original + 1, step_index)

    def test_run(self):
        test_method = MagicMock(return_value=True)
        values = {"piter": "pan", "king": "kong", "hannibal": "lector"}
        for k, v in values.items():
            self.sm.add_step(k, action=test_method, **{k: v})
        self.sm.run()

        for k, v in values.items():
            test_method.assert_any_call(**{k: v})

    def test_collect_warning(self):
        message = "The thread of human hope is spun with the flax of sorrow."
        count = 10
        test_method = MagicMock(return_value=(False, message))
        for i in range(0, count):
            self.sm.add_step(str(i)).add_expected(test_method)

        self.sm.run()

        warnings = self.sm.collect_warnings()

        self.assertTrue(self.sm.has_warnings())

        self.assertEqual(count, len(warnings))

    def test_collect_alert(self):
        message = "The fact that you have a place where you can return home, will lead you to happiness."
        count = 10
        test_method = MagicMock(return_value=(False, message))
        for i in range(0, count):
            self.sm.add_step(str(i)).add_expected(test_method, is_alert=True)

        self.sm.run()

        alerts = self.sm.collect_alerts()

        self.assertTrue(self.sm.has_alerts())

        self.assertEqual(count, len(alerts))

    def test_get_warnings(self):
        message = "The thread of human hope is spun with the flax of sorrow."
        test_method = MagicMock(return_value=(False, message))
        self.sm.add_step("warning").add_expected(test_method)
        self.sm.run()
        self.assertTrue(message in self.sm.get_warnings())

    def test_get_alerts(self):
        message = "The fact that you have a place where you can return home, will lead you to happiness."
        test_method = MagicMock(return_value=(False, message))
        self.sm.add_step("alert").add_expected(test_method, is_alert=True)
        self.sm.run()
        self.assertTrue(message in self.sm.get_alerts())


if __name__ == '__main__':
    unittest.main()
