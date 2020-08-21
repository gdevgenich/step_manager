import unittest
from datetime import datetime
from unittest.mock import MagicMock, Mock

from step_manager._Step import State, Step


class TestStep(unittest.TestCase):
    def setUp(self) -> None:
        self.name = "Kaworu"
        self.owner = Mock()
        self.owner.log = MagicMock()
        self.test_method = MagicMock(return_value=True)
        self.step = Step(self.owner, self.name, self.test_method)

    def test_step_name(self):
        self.assertEqual(self.name, self.step.name)

    def test_step_state(self):
        self.assertEqual(State.UNKNOWN, self.step.state)

    def test_action(self):
        self.assertEqual(self.test_method, self.step.action)

    def test_duration(self):
        duration = 5
        step = Step(self.owner, self.name, self.test_method, duration=duration)
        self.assertEqual(duration, step.duration)

    def test_set_duration(self):
        duration = 10
        step = Step(self.owner, self.name, self.test_method)
        step.set_duration(duration)
        self.assertEqual(duration, step.duration)

    def test_base_sm(self):
        self.assertEqual(None, self.step.sm)

    def test_sm_if_has_substeps(self):
        sm = Mock()
        sm.add_step = MagicMock()
        self.owner.createStepManager = MagicMock(return_value=sm)
        self.step.add_substep("Rei", self.test_method)
        self.assertEqual(sm, self.step.sm)

    def test_start_time(self):
        self.assertIsNone(self.step.start_time)

    def test_set_start_time(self):
        current_time = datetime.now()
        self.step.set_start_time(current_time)
        self.assertEqual(current_time, self.step.start_time)

    def test_stop_time(self):
        self.assertIsNone(self.step.stop_time)

    def test_set_stop_time(self):
        current_time = datetime.now()
        self.step.set_stop_time(current_time)
        self.assertEqual(current_time, self.step.stop_time)

    def test_run_with_exception(self):
        test_method = Mock(side_effect=IndexError('not found'))
        step = Step(self.owner, self.name, test_method)
        with self.assertRaises(IndexError):
            step.run()

        self.assertEqual(State.FAIL, step.state)

    def test_run_with_expected(self):
        first = "Unit-01"
        second = "Unit-02"
        test_method = MagicMock(return_value=True)
        expected_method = MagicMock(return_value=True)
        step = Step(self.owner, self.name, test_method, key=first)
        step.add_expected(expected_method, key=second)
        step.run()
        test_method.assert_called_with(key=first)
        expected_method.assert_called_with(key=second)
        self.assertEqual(State.PASS, step.state)

    def test_register_warning(self):
        message = "The thread of human hope is spun with the flax of sorrow."
        self.step.register_warning(message)
        warning = self.step.collect_warnings()
        self.assertIn("{}: {}".format(self.name, message), warning)

    def test_register_alerts(self):
        message = "The fact that you have a place where you can return home, will lead you to happiness."
        self.step.register_alert(message)
        alerts = self.step.collect_alerts()
        self.assertIn("{}: {}".format(self.name, message), alerts)

    def test_expected_attempts(self):
        first = "Unit-01"
        test_method = MagicMock(return_value=False)
        step = Step(self.owner, self.name, action=None, attempts=3)

        step.add_expected(test_method, key=first)
        step.run()
        test_method.assert_called_with(key=first)
        self.assertTrue(step.repeat)


if __name__ == '__main__':
    unittest.main()
