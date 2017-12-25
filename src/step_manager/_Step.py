#

from __future__ import absolute_import

import logging

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

    def __init__(self, owner, name, action, duration=0.0, **kwargs):
        self._owner = owner
        self._name = name
        self._action = action
        self._kwargs = kwargs
        self._sm = None
        self._duration = duration
        self._expected = list()
        self.warnings = list()
        self.start_time = None
        self.end_time = None
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

    def add_substep(self, name, action=None, duration=0.0, **kwargs):
        if self._sm is None:
            self._sm = self._owner.createStepManager()
        step = self._sm.add_step(name=name, action=action, duration=duration, **kwargs)
        return step


    def add_expected(self, expected, **kwargs):
        kwargs["__method__"] = expected
        self._expected.append(kwargs) # TODO - Why you does not create a class? Do you have any class limitations? Reason mixing two different kind of instances?
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
            if self._action:
                self._action(**self._kwargs)

            self._state = State.PASS
        except:
            self._state = State.FAIL
            raise

        # Step 2. Collect expected messages
        for kwargs in self._expected:
            method = kwargs.pop("__method__")
            self._owner.log(logging.INFO, "Check expected '{method}' with params {params}".format(method=method.__name__, params=kwargs))
            try:
                res, message = method(**kwargs)
                if not res:
                    self._owner.log( logging.ERROR,
                                     "Check of expected '{method}' with params {params} failed with message {message}"
                                     .format(method=method.__name__, params=kwargs,message=message))
                    self.register_warning(message)
                    self._state = State.WARN
                else:
                    self._owner.log(logging.INFO,
                                    "Check expected '{method}' with params {params} passed".format(method=method.__name__, params=kwargs))
            except Exception as err:
                self._owner.log(logging.ERROR,
                                "Check expected '{method}' with params {params} failed with exception {err}".
                                format(method=method.__name__, params=kwargs, err=err))
                self.register_warning(repr(err))
                self._state = State.BROK
