import unittest


if __name__ == "__main__":
    loader = unittest.TestLoader()
    tests = loader.discover('.', pattern='test_*.py')
    testRunner = unittest.runner.TextTestRunner()
    testRunner.run(tests)
    