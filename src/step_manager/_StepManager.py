#

from __future__ import absolute_import

from sys import stdout
import logging
from copy import copy

from reactor import Reactor

from ._Step import Step


class StepManager(object):
    """
    @ivar bool careful: Determine careful duration calculation (without except action run)
    """

    def __init__(self, careful=False):
        self._log = logging.getLogger("step_manager")
        self._steps = list()
        self._backlog = list()
        self._completed = False
        self._exec_after = None
        self.__warnings = list()
        self._duration = 0.0
        self._careful = careful
        self.level = 0

    @property
    def completed(self):
        return self._completed

    def log(self, level, message):
        message="+"*self.level+message
        self._log.log(level=level, msg=message)

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
        raise Exception("No step with name {name} found".format(name=name))

    def add_substep(self, step_name, substep_name, action=None, duration=0.0, **kwargs):
        step = self.find_step(name=step_name)
        step.add_substep(name=substep_name, action=action, duration=duration, **kwargs)

    @staticmethod
    def createStepManager():
        return StepManager()

    def add_step(self, name, action=None, duration=0.0, **kwargs):
        step = Step(owner=self, name=name, action=action, duration=duration, **kwargs)
        self._steps.append(step)
        return step

    def remove_step(self, step_name):
        self._steps.remove(self.find_step(step_name))

    def add_step_after(self, after_step, name, action=None, duration=0.0, **kwargs):
        after_step_index = self.find_step_index(after_step)
        if after_step_index == -1:
            raise ValueError("No step with name {after_step} registered in step manager".format(after_step=after_step))
        step = Step(self, name, action, duration, **kwargs)
        self._steps.insert(after_step_index+1, step)
        return step

    def run(self, timeout=180):
        react = Reactor()
        react.call_later(0.0, self.start)
        react.run(timeout)

    def start(self, reactor):
        self._backlog = list(self._steps)
        reactor.call_later(0.0, self._iteration)

    def has_warnings(self):
        self.collect_warnings()
        if len(self.__warnings) > 0:
            return True
        else:
            return False

    def collect_warnings(self):
        if len(self.__warnings) > 0:
            return self.__warnings
        for step in self._steps:
            step_warnings = step.collect_warnings()
            for warning in step_warnings:
                self.__warnings.append(warning)
        return self.__warnings

    def get_warnings(self):
        self.collect_warnings()
        if not self._completed:
            self.__warnings.append("Step manager wasn't completed")
        warning_string = ""
        for warning in self.__warnings:
            warning_string+="\n"+warning
        return warning_string

    def _iteration(self, reactor):
        if len(self._backlog) == 0:
            self.stop(reactor)
        else:
            step = self._backlog.pop(0)
            self.log(logging.INFO, "'{name}' step execution started".format(name=step.name))

            step.set_start_time(reactor.seconds())
            try:
                step.run()
            except Exception as err:
                self.log(logging.ERROR, "'{name}' step execution filed with next exception".format(name=step.name))
                self.log(logging.ERROR, err)
                raise
            else:
                step.set_stop_time(reactor.seconds())
                self.log(logging.INFO, "'{name}' step execution finished took {sec} seconds".
                                format(name=step.name, sec=step.stop_time-step.start_time))

            if self._careful:
                new_duration = step.duration - step.seconds  # TODO - careful about negative value ...
            else:
                new_duration = step.duration

            if step.sm is not None:
                step.sm.level = self.level+1
                self.log(logging.INFO, "Substeps from step with name '{name}' started".format(name=step.name, time=reactor.seconds()))
                step.sm.set_exec_after(self._iteration)
                step.sm.set_duration(step.duration)
                reactor.call_later(0.0, step.sm.start)
            else:
                reactor.call_later(new_duration, self._iteration)

    def stop(self, reactor):
        self._completed = True
        if self._exec_after is None:
            self.log(logging.INFO, "Main Step Manager finished work at reactor time {time}".format(time=reactor.seconds()))
            reactor.stop()
        else:
            self.log(logging.INFO, "Substeps sequence finished work at reactor time {time}".format(time=reactor.seconds()))
            reactor.call_later(self._duration, self._exec_after)

    def dump(self, level=0, base_order=None, stream=None):

        if not stream:
            stream = stdout

        if not base_order:
            base_order = []

        for number, s in enumerate(self._steps):
            padding = " + " * level
            order = copy(base_order)
            order.append(str(number+1))
            step_number = ".".join(order)
            step_name = s._name
            step_action = s.action
            step_expecteds = s._expected
            step_duration = s.duration
            step_state = s.state
            msg = "{padding} {step_number}. {step_name} [{state}] (action={step_action!r} expecteds={step_expecteds!r} duration={step_duration!r})\n".format(padding=padding, step_number=step_number, step_name=step_name, state=step_state, step_action=step_action, step_expecteds=step_expecteds, step_duration=step_duration)
            stream.write(msg)
            if s.sm:
                s.sm.dump(level=level+1, base_order=order, stream=stream)
