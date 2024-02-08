import inspect

def test_every_function():
    # Get a list of all functions in the module and test module
    module_functions = [f[0] for f in inspect.getmembers(app, inspect.isfunction)]
    test_functions = [f[0] for f in inspect.getmembers(tests, inspect.isfunction)]

    # Check that for every function in the module, there is a corresponding test function
    untested_functions = []
    for function in module_functions:
        test_function = 'test_' + function
        if test_function not in test_functions:
            untested_functions.append(function)
            with open('untested_functions.txt', 'a') as file:
                file.write(f"No test function found for {function}\n")

    # Continue the loop even if there are untested functions
    # ...

test_every_function()