from step_manager.pbxut import StepTestCase


class SimpleTest(StepTestCase):
    """
    @name: Simple test
    """

    def setUp(self):
        pass
    
    def test_method(self):
        print ("Hello, World!")

    def initialize(self, sm):

        sm.add_step("Test", self.test_method)

    def tearDown(self):
        pass



