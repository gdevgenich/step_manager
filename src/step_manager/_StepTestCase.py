#

from __future__ import absolute_import

from pbxut import PBXTestCase
from abc import ABCMeta, abstractmethod

from ._StepManager import StepManager


class StepTestCase(PBXTestCase):

    __metaclass__ = ABCMeta
    __sm__ = None


    def prepareReport(self, sm):
        result = "Huh... This is report."
        return result


    def assertTrue(self, actual, msg=None):

        if actual != True:
            err = AssertionError(msg)
            err.content = self.prepareReport(self.__sm__)


    @abstractmethod
    def initialize(self, sm):
        raise NotImplementedError()


    def runTest(self):
       self.__sm__ = StepManager()
       self.initialize(self.__sm__)
       self.__sm__.run()
