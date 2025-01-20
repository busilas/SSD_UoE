import unittest
from cli import CLI

class CLITestCase(unittest.TestCase):
    def test_cli_startup(self):
        cli = CLI()
        self.assertIsNone(cli.current_user)

if __name__ == '__main__':
    unittest.main()
