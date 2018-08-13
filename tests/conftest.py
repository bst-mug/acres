import pytest

from acres.preprocess import resource_factory


@pytest.fixture(scope="module", autouse=True)
def path_resource_factory():
    resource_factory.PICKLE_FOLDER = "tests/models/pickle/"
    resource_factory.NGRAMS_FOLDER = "tests/models/ngrams/"
    resource_factory.LOG_FOLDER = "tests/models/log/"
    resource_factory.NN_MODELS_FOLDER = "tests/models/nn/"
    resource_factory.DATA_FOLDER = "tests/data"
