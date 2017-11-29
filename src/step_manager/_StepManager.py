#

from __future__ import absolute_import

from logging import getLogger
from copy import copy

from reactor import Reactor

from ._Step import Step


class StepManager(object):

    def __init__(self, name):
        self.__log = getLogger("step_manager")
        self._name = name
        self._steps = list()
        self._backlog = list()
        self._completed = False
        self._exec_after = None
        self.__warnings = None
        self._duration = 0.0

    @property
    def completed(self):
        return self._completed

    def set_duration(self, duration):
        self._duration = duration

    def get_duration(self):
        return self._duration

    def set_exec_after(self, exec_after):
        self._exec_after = exec_after

    def get_exec_after(self):
        return self._exec_after

    def find_step_index(self, name):
        for i in range(len(self._steps)):
            if self._steps[i].name == name:
                return i
        return -1

    def find_step(self, name):
        for step in self._steps:
            if step.name == name:
                return step
        return None

    def add_substep(self, step_name, substep_name, sm):
        step_index = self.find_step_index(name=step_name)
        if step_index == -1:
            raise ValueError("No step with name {step_name} registered in step manager".format(step_name=step_name))
        self._steps[step_index].add_substep(substep_name, sm)

    @staticmethod
    def createStepManager(name):
        return StepManager(name=name)

    def add_step(self, name, action, duration=0.0):
        step = Step(owner=self, name=name, action=action, duration=duration)
        self._steps.append(step)
        return step

    def remove_step(self, step_name):
        step = self.find_step(step_name)
        if step is None:
            raise ValueError("No such step registered in system")

    def add_step_after(self, after_step, step):
        after_step_index = self.find_step_index(after_step)
        if after_step_index == -1:
            raise ValueError("No step with name {after_step} registered in step manager".format(after_step=after_step))
        self._steps.insert(after_step_index, step)

    def run(self, timeout=180):
        react = Reactor()
        react.call_later(0.0, self.start)
        react.run(timeout)

    def start(self, reactor):
        self._backlog = list(self._steps)
        reactor.call_later(0.0, self._iteration)

    def has_warnings(self):
        if self.__warnings is None:
            self.collect_warnings()
        if len(self.__warnings["warnings"]) > 0:
            return True
        else:
            return False

    def collect_warnings(self):
        if self.__warnings is None:
            self.__warnings = {"name": self._name, "warnings":[]}
            for step in self._steps:
                if isinstance(step.action, StepManager):
                    step_warnings = step.action.collect_warnings()
                else:
                    step_warnings = step.collect_warnings()
                if len(step_warnings["warnings"]) > 0:
                    self.__warnings["warnings"].append(step_warnings)
        return self.__warnings

    def _iteration(self, reactor):
        if len(self._backlog) == 0:
            self.stop(reactor)
        else:
            step = self._backlog.pop(0)
            if isinstance(step.action, StepManager):
                self.__log.info("Step manager  from step with name '{name}' started".format(name=step.name))
                step.action.set_exec_after(self._iteration)
                step.action.start(reactor)
            else:
                self.__log.info("Step with name '{name}' started".format(name=step.name))
                step.run()
                if step.sm is not None:
                    self.__log.info("Step manager from step with name '{name}' started".format(name=step.name))
                    step.sm.set_exec_after(self._iteration)
                    step.sm.set_duration(step.duration)
                    reactor.call_later(0.0, step.sm.start)
                else:
                    reactor.call_later(step.duration, self._iteration)

    def stop(self, reactor):
        self._completed = True
        if self._exec_after is None:
            self.__log.info("Main Step Manager finished work")
            reactor.stop()
        else:
            self.__log.info("Embedded Step Manager finished work")
            reactor.call_later(self._duration, self._exec_after)

    def dump(self, level=0, base_order=None):

        if not base_order:
            base_order = []

        for number, s in enumerate(self._steps):
            padding = " + " * level
            order = copy(base_order)
            order.append(str(number+1))
            step_number = ".".join(order)
            step_name = s._name
            step_action = s.action
            step_expecteds = "TODO"
            step_duration = s.duration
            print("{padding} {step_number}. {step_name} (action={step_action!r} expecteds={step_expecteds!r} duration={step_duration!r})".format(padding=padding, step_number=step_number, step_name=step_name, step_action=step_action, step_expecteds=step_expecteds, step_duration=step_duration))
            if s.sm:
                s.sm.dump(level=level+1, base_order=order)
