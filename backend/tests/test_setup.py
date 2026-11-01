def test_environment_is_working():
    assert 1 + 1 == 2


def test_python_version():
    import sys

    assert sys.version_info.major == 3
    assert sys.version_info.minor == 12
