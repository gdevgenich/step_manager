
class StepTestCase(PBXTestCase):

    def assertFalse(self):

        err = AssertionError('')
        err.content = self.content

        raise err

    def initialize(self, sm):
        raise NotImplementedError()

    def runTest(self):
       sm = StepManager()
       self.initialize(sm)
       sm.run()
