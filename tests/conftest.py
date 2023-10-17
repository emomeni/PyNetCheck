DIR = None


def pytest_addoption(parser):
    parser.addoption("--dir", action="store")


def pytest_configure(config):
    global DIR
    DIR = config.getoption("--dir")
