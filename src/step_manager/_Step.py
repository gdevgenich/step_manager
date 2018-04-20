#

from __future__ import absolute_import

import logging
from ._Expected import Expected

class State(object):
    UNKNOWN = "unknown"
    PASS = "passed"
    FAIL = "failed"
    WARN = "warned"
    BROK = "broken"


class Step(object):
    """
    @ivar StepManager _owner:
    """

    def __init__(self, owner, name, action, duration=0.0, interval=0, attempts=1, throw_except=False, **kwargs):
        self._owner = owner
        self.log = owner.log
        self._name = name
        self._action = action
        self._kwargs = kwargs
        self.interval = interval
        self._left_attempts = attempts
        self.repeat = False
        self._action_executed = False
        self._sm = None
        self._duration = duration
        self._expected = list()
        self.warnings = list()
        self.start_time = None
        self.end_time = None
        self.start_info_provided = False
        self.throw_except = throw_except
        self._state = State.UNKNOWN

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def seconds(self):
        result = 0
        if all([self.start_time, self.stop_time]):
            result = self.stop_time - self.start_time
        return result

    @property
    def duration(self):
        return self._duration

    @property
    def action(self):
        return self._action

    @property
    def sm(self):
        return self._sm

    def set_start_time(self, start_time):
        self.start_time = start_time

    def set_stop_time(self, stop_time):
        self.stop_time = stop_time

    def get_start_time(self):
        return self.start_time

    def get_stop_time(self):
        return self.stop_time

    def add_substep(self, name, action=None, duration=0.0, interval=0, attempts=1, throw_except=False, **kwargs):
        if self._sm is None:
            self._sm = self._owner.createStepManager()
        step = self._sm.add_step(name=name, action=action, duration=duration, interval=interval, attempts=attempts, throw_except=throw_except, **kwargs)
        return step

    def add_expected(self, method, **kwargs):
        self._expected.append(Expected(owner=self, method=method, **kwargs))
        return self

    def register_warning(self, msg):
        self.warnings.append("{step}: {msg}".format(step=self.name, msg=msg))

    def collect_warnings(self):
        if len(self.warnings) > 0:
            return self.warnings
        if self.sm is not None:
            sm_warnings = self.sm.collect_warnings()
            for msg in sm_warnings:
                self.register_warning(msg=msg)
        return self.warnings

    def run(self):
        # Step 1. Execute action in critical section
        try:
            if self._action and not self._action_executed:
                if hasattr(self._action, '__name__'):
                    action_name = self._action.__name__
                else:
                    action_name = self._action
                self.log(logging.INFO, ".Action {action} with params {params} started"
                                .format(action=action_name, params=self._kwargs))
                self._action_executed = True
                self._action(**self._kwargs)
                self.log(logging.INFO, ".Action completed")
            self._state = State.PASS
        except Exception as err:
            self._state = State.FAIL
            self.log(logging.ERROR, "!Action failed with exception: {err}".format(err=err.message))
            raise

        # Step 2. Collect expected messages
        self.repeat = False
        self._left_attempts -= 1
        for expected in self._expected:
            try:
                res, message = expected.run()
                if not res and self._left_attempts == 0:
                    self.log(logging.WARNING, "!Check of expected in step {step_name} failed with message: {message}"
                             .format(step_name=self._name, message=message))
                    self.register_warning(message)
                    self._state = State.WARN
                    if self.throw_except:
                        raise AssertionError("!Check of expected in step {step_name} failed with message: {message}"
                             .format(step_name=self._name, message=message))
                elif not res:
                    self.repeat = True
            except Exception as err:
                self.log(logging.ERROR, "!Check failed with exception: {err}".format(err=err))
                self.register_warning(repr(err))
                self._state = State.BROK
                raise

