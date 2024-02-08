import unittest
import inspect
import sys
sys.path.append('/Users/tylerpeairs/SoftwareProjects/TestChatbot/python-whatsapp-bot/')

import app
import tests



def test_every_function():
    # Get a list of all functions in the module and test module
    module_functions = [f[0] for f in inspect.getmembers(app, inspect.isfunction)]
    test_functions = [f[0] for f in inspect.getmembers(tests, inspect.isfunction)]
    untested_functions = []

    # Check that for every function in the module, there is a corresponding test function
    for function in module_functions:
        test_function = 'test_' + function
        if test_function not in test_functions:
            untested_functions.append(function)

    # Write all untested functions to the file outside the loop
    with open('untested_functions.txt', 'w') as file:  # Consider using 'w' to overwrite each time or 'a' to append
        for function in untested_functions:
            file.write(f"No test function found for {function}\n")

if __name__ == "__main__":
    loader = unittest.TestLoader()
    tests = loader.discover('.', pattern='test_*.py')
    for test in tests:
        print(test)
    testRunner = unittest.runner.TextTestRunner()
    test_every_function()
    testRunner.run(tests)


