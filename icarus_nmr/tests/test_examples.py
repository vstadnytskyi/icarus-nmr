def test_one_plus_one_is_two():
    "Check that one and one are indeed two."
    assert 1 + 1 == 2
def test_print_current_dir():
    from os import getcwd, listdir
    print('project root dir',getcwd())
    print('project list dir',listdir())
