#

from __future__ import absolute_import

from pbxut import PBXTestCase
from abc import ABCMeta, abstractmethod

from six import StringIO

from ._StepManager import StepManager


class StepTestCase(PBXTestCase):

    __metaclass__ = ABCMeta
    __sm__ = None

    CAREFUL = True


    def prepareReport(self, sm):
        stream = StringIO()
        sm.dump(stream=stream) # TODO - more color ...
        result = stream.getvalue()
        return result


    def assertTrue(self, actual, msg=None):

        if actual != True:
            err = AssertionError(msg)
            err.content = self.prepareReport(self.__sm__)
            raise err


    @abstractmethod
    def initialize(self, sm):
        raise NotImplementedError()


    def runTest(self):
       self.__sm__ = StepManager(careful=self.CAREFUL)
       self.initialize(self.__sm__)
       self.__sm__.run()
