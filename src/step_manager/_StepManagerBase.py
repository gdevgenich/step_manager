

class StepManagerBase(object):
    def __init__(self):
        self._exec_after = None

    def start(self):
        pass

    def stop(self):
        self._completed = True
        if self._exec_after is None:
            self.__log.info("Main Step Manager finished work at reactor time {time}".format(time=reactor.seconds()))
            reactor.stop()
        else:
            self.__log.info("Substeps sequence finished work at reactor time {time}".format(time=reactor.seconds()))
            reactor.call_later(self._duration, self._exec_after)
