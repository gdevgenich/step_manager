
from pbxut import PBXTestSuite

class SomeSuite(PBXTestSuite):
    def setUpSuite(self):
        print("Start suite")

    def tearDownSuite(self):
        print("Stop suite")