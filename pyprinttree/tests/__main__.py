import os
import unittest


suite = unittest.TestLoader().discover(os.path.abspath(os.path.dirname(__file__)))
suite.run(unittest.TestResult())
