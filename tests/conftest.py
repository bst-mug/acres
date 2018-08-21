import pytest

from acres.preprocess import resource_factory


@pytest.fixture(scope="module", autouse=True)
def path_resource_factory():
    resource_factory.PICKLE_FOLDER = "tests/models/pickle/"
    resource_factory.NGRAMS_FOLDER = "tests/models/ngrams/"
    resource_factory.LOG_FOLDER = "tests/models/log/"
    resource_factory.NN_MODELS_FOLDER = "tests/models/nn/"
    resource_factory.DATA_FOLDER = "tests/data"
    resource_factory.reset()


@pytest.fixture(scope="module")
def ngramstat():
    # Setup: save current one and assign a fake one
    old = resource_factory.NGRAMSTAT
    resource_factory.NGRAMSTAT = {1: (200, "der"), 2: (50, "EKG"), 3: (20, "Im EKG")}
    yield resource_factory.NGRAMSTAT

    # Teardown: revert back to old
    resource_factory.NGRAMSTAT = old
