from __future__ import absolute_import

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
        self._expected = dict()
        self.warnings = list()

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

    def add_substep(self, name, action=None, duration=0.0, **kwargs):
        if self._sm is None:
            self._sm = self._owner.createStepManager()
        step = self._sm.add_step(name=name, action=action, duration=duration, **kwargs)
        return step

    def add_expected(self, expected, **kwargs):
        self._expected[expected] = kwargs
        return self

    def register_warning(self, msg):
        self.warnings.append("{step}: {msg}".format(step=self.name, msg=msg))

    def collect_warnings(self):
        if self.sm is not None:
            sm_warnings = self.sm.collect_warnings()
            for msg in sm_warnings:
                self.register_warning(msg=msg)
        return self.warnings

    def run(self):
        if self._action is not None:
            self._action(**self._kwargs)
        for exp, kwargs in self._expected.items():
            res, message = exp(**kwargs)
            if not res:
                self.register_warning(message)
