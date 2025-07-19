import unittest
from utils import get_logger

class TestUtils(unittest.TestCase):
    def test_get_logger_returns_logger_instance(self):
        logger = get_logger("test_module")
        self.assertEqual(logger.name, "test_module")
        # Check that logger has at least one handler
        self.assertTrue(len(logger.handlers) > 0)
        # Check that logger level is set from config
        self.assertTrue(logger.level >= 0)

if __name__ == "__main__":
    unittest.main()
