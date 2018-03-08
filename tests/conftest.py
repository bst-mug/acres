import pytest

from acres import resource_factory


@pytest.fixture(scope="session", autouse=True)
def execute_before_any_test():
    resource_factory.PICKLE_FOLDER = "tests/" + resource_factory.PICKLE_FOLDER
    resource_factory.LOG_FOLDER = "tests/" + resource_factory.LOG_FOLDER
