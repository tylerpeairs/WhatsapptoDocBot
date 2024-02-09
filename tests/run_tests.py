import unittest


if __name__ == "__main__":
    loader = unittest.TestLoader()
    tests = loader.discover('.', pattern='test_*.py')
    output_file = "/Users/tylerpeairs/SoftwareProjects/TestChatbot/python-whatsapp-bot/tests/test_output.txt"
    with open(output_file, "w") as file:
        testRunner = unittest.runner.TextTestRunner(stream=file)
        testRunner.run(tests)
    