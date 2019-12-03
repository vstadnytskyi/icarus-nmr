def test_one_plus_one_is_two():
    "Check that one and one are indeed two."
    assert 1 + 1 == 2

import unittest
class QueueTest(unittest.TestCase):
    def test_print_current_dir(self):
        from os import getcwd, listdir
        self.assertEqual('project root dir',getcwd())

    def test_print_list_dir(self):
        from os import getcwd, listdir
        self.assertEqual('project list dir',listdir())
