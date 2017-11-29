from __future__ import absolute_import

class Step(object):
    """
    @ivar StepManager _owner:
    """

    def __init__(self, owner, name, action, duration=0.0):
        self._owner = owner
        self._name = name
        self._action = action
        self._sm = None
        self._duration = duration
        self._expected = dict()
        self.warnings = {"name": self.name, "warnings": []}

    @property
    def name(self):
        return self._name

    @property
    def duration(self):
        return self._duration

    @property
    def action(self):
        return self._action

    @property
    def sm(self):
        return self._sm

    def add_substep(self, name, action=None):
        if self._sm is None:
            self._sm = self._owner.createStepManager(name)
        self._sm.add_step(name=name, action=action, duration=0.0)
        return self._sm

    def add_expected(self, expected, **kwargs):
        self._expected[expected] = kwargs
        return self

    def register_warning(self, msg):
        self.warnings["warnings"].append(msg)

    def collect_warnings(self):
        if self.sm is not None:
            sm_warnings = self.sm.collect_warnings()
            if len(sm_warnings["warnings"]) > 0:
                self.warnings["warnings"].append(sm_warnings)
        return self.warnings

    def run(self):
        if self._action is not None:
            self._action()
        for exp, kwargs in self._expected.items():
            message = exp(**kwargs)
            if message is not None:
                self.register_warning(message)
