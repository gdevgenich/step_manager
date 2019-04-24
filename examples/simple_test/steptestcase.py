#!/usr/bin/python3

from logging import basicConfig, DEBUG

from pbxut import PBXTestRunner
from pbxut.loaders.directory import DirectoryTestLoader


if __name__ == "__main__":
    basicConfig(filename="debug.log", level=DEBUG)
    #
    runner = PBXTestRunner(loader=DirectoryTestLoader(), failfast=False)
    runner.run()