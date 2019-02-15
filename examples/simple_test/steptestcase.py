from pbxut import PBXTestRunner
from pbxut.loaders.directory import DirectoryTestLoader


if __name__ == "__main__":
    runner = PBXTestRunner(loader=DirectoryTestLoader(), failfast=False)
    
    runner.run()