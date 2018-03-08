import pytest

from acres import resource_factory


@pytest.fixture(scope="session", autouse=True)
def execute_before_any_test():
    resource_factory.ROOT_FOLDER = "tests/" + resource_factory.ROOT_FOLDER
