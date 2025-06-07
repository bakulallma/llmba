import unittest

class TestSanity(unittest.TestCase):
    def test_basic_assertion(self):
        self.assertTrue(True, "This basic assertion should always pass.")

if __name__ == '__main__':
    unittest.main()
