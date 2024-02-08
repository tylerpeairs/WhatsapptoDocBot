import unittest


if __name__ == "__main__":
    loader = unittest.TestLoader()
    tests = loader.discover('.', pattern='test_*.py')
    for test in tests:
        print(test)
    testRunner = unittest.runner.TextTestRunner()
    testRunner.run(tests)


