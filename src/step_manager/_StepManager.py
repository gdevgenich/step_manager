#

from __future__ import absolute_import

from sys import stdout
import logging
from copy import copy
from datetime import datetime

from reactor import Reactor

from ._Step import Step


class StepManager(object):
    """
    @ivar bool careful: Determine careful duration calculation (without except action run)
    """

    def __init__(self, careful=False, unfinished_except=True):
        self._log = logging.getLogger("step_manager")
        self._steps = list()
        self._backlog = list()
        self._completed = False
        self._exec_after = None
        self.__warnings = list()
        self.__alerts = list()
        self._duration = 0.0
        self._context = dict()
        self._careful = careful
        self._unfinished_except = unfinished_except
        self.level = 0

    @property
    def completed(self):
        return self._completed

    def log(self, level, message):
        message = ".." * self.level + str(message)
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

    def find_last_step_index(self, name):
        step = -1
        for i in range(len(self._steps)):
            if self._steps[i].name == name:
                step = i
        return step

    def find_step(self, name):
        for step in self._steps:
            if step.name == name:
                return step
        raise Exception("No step with name {name} found".format(name=name))
    
    def rfind_step(self, name):
        for step in reversed(self._steps):
            if step.name == name:
                return step
        raise Exception("No step with name {name} found".format(name=name))

    def find_steps(self, name):
        steps = list()
        for step in self._steps:
            if step.name == name:
                steps.append(step)
        if len(steps) == 0:
            raise Exception("No step with name {name} found".format(name=name))
        else:
            return steps

    def add_substep(self, step_name, substep_name, action=None, duration=0.0, interval=0, attempts=1,
                    throw_except=False, **kwargs):
        start = datetime.now()
        self._log.debug("Try to add substep to step with name {step_name} at {start}".format(step_name=step_name,
                                                                                             start=start))
        step = self.find_step(name=step_name)
        substep_step = step.add_substep(name=substep_name, action=action, duration=duration,
                                        interval=interval, attempts=attempts,
                                        throw_except=throw_except, **kwargs)
        stop = datetime.now()
        took = stop - start
        self._log.debug("Step added took {took}".format(took=took))
        return substep_step

    @staticmethod
    def createStepManager():
        return StepManager()

    def add_step(self, name, action=None, duration=0.0, interval=0, attempts=1, throw_except=False, **kwargs):
        start = datetime.now()
        self._log.debug("Try to add step with name {step_name} at {start}".format(step_name=name, start=start))
        step = Step(owner=self, name=name, action=action, duration=duration, interval=interval, attempts=attempts,
                    throw_except=throw_except, **kwargs)
        self._steps.append(step)
        stop = datetime.now()
        took = stop-start
        self._log.debug("Step added took {took}".format(took=took))
        return step

    def remove_step(self, step_name):
        self._steps.remove(self.find_step(step_name))
    
    def remove_step_from_bottom(self, step_name):
        self._steps.remove(self.rfind_step(step_name))

    def add_step_after(self, after_step, name, action=None, duration=0.0, **kwargs):
        start = datetime.now()
        self._log.debug("Try to add step with name {step_name} after step {after_step} at {start}".
                        format(step_name=name, after_step=after_step, start=start))
        after_step_index = self.find_last_step_index(after_step)
        if after_step_index == -1:
            raise ValueError("No step with name {after_step} registered in step manager".format(after_step=after_step))
        step = Step(self, name, action, duration, **kwargs)
        self._steps.insert(after_step_index + 1, step)
        stop = datetime.now()
        took = stop - start
        self._log.debug("Step added took {took}".format(took=took))
        return step
    
    def add_step_before(self, before_step, name, action=None, duration=0.0, **kwargs):
        start = datetime.now()
        self._log.debug("Try to add step with name {step_name} before step {before_step} at {start}".
                        format(step_name=name, before_step=before_step, start=start))
        before_step_index = self.find_last_step_index(before_step)
        if before_step_index == -1:
            raise ValueError("No step with name {before_step} registered in step manager".format(before_step=before_step))
        step = Step(self, name, action, duration, **kwargs)
        self._steps.insert(before_step_index, step)
        stop = datetime.now()
        took = stop - start
        self._log.debug("Step added took {took}".format(took=took))
        return step

    def run(self, timeout=180):
        react = Reactor()
        react.call_later(0.0, self.start)
        react.run(timeout)
        if not self._completed:
            if self._unfinished_except:
                raise Exception("StepManager finished because of timeout")
            else:
                self.collect_warnings()
                self.__warnings.append("StepManager finished because of timeout")

    def start(self, reactor):
        self._backlog = list(self._steps)
        reactor.call_later(0.0, self._iteration)

    def continue_execution(self, timeout=180):
        react = Reactor()
        react.call_later(0.0, self._continue_exection)
        react.run(timeout)
    
    def update_backlog(self):
        for step in self._steps:
            if not step.start_info_provided:
                self._backlog.append(step)

    def _continue_exection(self, reactor):
        self._backlog = list()
        for step in self._steps:
            if not step.start_info_provided:
                self._backlog.append(step)
        reactor.call_later(0.0, self._iteration)

    def has_warnings(self):
        self.collect_warnings()
        if len(self.__warnings) > 0:
            return True
        else:
            return False

    def has_alerts(self):
        self.collect_alerts()
        if len(self.__alerts) > 0:
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

    def collect_alerts(self):
        if len(self.__alerts) > 0:
            return self.__alerts
        for step in self._steps:
            step_alerts = step.collect_alerts()
            for alert in step_alerts:
                self.__alerts.append(alert)
        return self.__alerts

    def get_warnings(self):
        self.collect_warnings()
        if not self._completed:
            self.__warnings.append("Step manager wasn't completed")
        warning_string = ""
        for warning in self.__warnings:
            warning_string += "\n" + warning
        return warning_string

    def get_alerts(self):
        self.collect_alerts()
        alerts_string = ""
        for alert in self.__alerts:
            alerts_string += "\n" + alert
        return alerts_string

    def _iteration(self, reactor):
        # If no step left then reactor should be stopped
        if len(self._backlog) == 0:
            self.stop(reactor)
        else:
            # Get first step in queue
            step = self._backlog[0]
            if not step.start_info_provided:
                step.start_info_provided = True
                self.log(logging.INFO, "{name} :: step execution started".format(name=step.name))
            # Save reactor start time for step
            if step.start_time is None:
                step.set_start_time(reactor.seconds())
            try:
                # Run step
                step.run()
            except Exception as err:
                self.log(logging.ERROR,
                         "{name} :: step execution failed, reason: {err!r}".format(name=step.name, err=err))
                raise
            else:
                if not step.repeat:
                    # Save step stop time if no exceptions happen
                    step.set_stop_time(reactor.seconds())
                    self.log(logging.INFO, "{name} :: step execution finished in {sec} seconds".
                             format(name=step.name, sec="%.3f" % (step.stop_time - step.start_time)))
            if step.repeat:
                reactor.call_later(step.interval, self._iteration)
            else:
                if self._careful:
                    new_duration = step.duration - step.seconds
                else:
                    new_duration = step.duration
                # If step has substeps then run start step manager with substeps
                if step.sm is not None:
                    step.sm.level = self.level + 1
                    self.log(logging.INFO, ".Substeps from step with name '{name}' started".
                             format(name=step.name, time="%.3f" % reactor.seconds()))
                    step.sm.set_exec_after(self._iteration)
                    # Careful with timeout between steps
                    step.sm.set_duration(step.duration)
                    self._backlog.pop(0)
                    reactor.call_later(0.0, step.sm.start)
                else:
                    self.log(logging.INFO,
                             ".Next step will be started after {dur} seconds timeout".format(dur=new_duration))
                    self._backlog.pop(0)
                    reactor.call_later(new_duration, self._iteration)

    def stop(self, reactor):
        self._completed = True
        if self._exec_after is None:
            self.log(logging.INFO,
                     "Main Step Manager finished work at reactor time {time}".format(time="%.2f" % reactor.seconds()))
            reactor.stop()
        else:
            # self.level -= 1  TODO: decrease indentation after subsequence is completed
            self.log(logging.INFO,
                     ".Substeps sequence finished work at reactor time {time}".format(time="%.2f" % reactor.seconds()))
            self.log(logging.INFO,
                     ".Next step will be started after {dur} seconds timeout".format(dur=self._duration))
            reactor.call_later(self._duration, self._exec_after)

    def dump(self, level=0, base_order=None, stream=None):

        if not stream:
            stream = stdout

        if not base_order:
            base_order = []

        for number, s in enumerate(self._steps):
            padding = ".." * level
            order = copy(base_order)
            order.append(str(number + 1))
            step_number = ".".join(order)
            step_name = s._name
            step_action = s.action
            step_expecteds = s._expected
            step_duration = s.duration
            step_state = s.state
            msg = "{padding} {step_number}. {step_name} [{state}] (action={step_action!r} expecteds={step_expecteds!r} duration={step_duration!r})\n".format(
                padding=padding, step_number=step_number, step_name=step_name, state=step_state,
                step_action=step_action, step_expecteds=step_expecteds, step_duration=step_duration)
            stream.write(msg)
            if s.sm:
                s.sm.dump(level=level + 1, base_order=order, stream=stream)

    def get(self, key):
        res = self._context.get(key)
        # if res is None:
        #     raise ValueError("No key {key} was stored".format(key=key))
        # else:
        return res

    def set(self, key, value):
        if callable(value):
            value = value()
        self._context[key] = value

    def add_to_dict(self, dict_name, key, value):
        if callable(value):
            value = value()
        if dict_name in self._context:
            self._context.get(dict_name)[key] = value
        else:
            self._context[dict_name] = dict((key, value))

    def add_to_list(self, list_name, value):
        if callable(value):
            value = value()
        if list_name in self._context:
            self._context.get(list_name).append(value)
        else:
            self._context[list_name] = list(value)

    def call_method_of_stored_value(self, key, method_name, **kwargs):
        link_to_method = getattr(self.get(key), method_name)
        return link_to_method(**kwargs)