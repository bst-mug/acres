import pytest

from acres.preprocess import resource_factory
from acres.util import functions


@pytest.fixture(scope="module", autouse=True)
def path_resource_factory():
    resource_factory.PICKLE_FOLDER = "models/pickle/"
    resource_factory.NGRAMS_FOLDER = "models/ngrams/"
    resource_factory.LOG_FOLDER = "models/log/"
    resource_factory.NN_MODELS_FOLDER = "models/nn/"
    resource_factory.DATA_FOLDER = functions.import_conf("CORPUS_PATH")
    print("WARNING: Switched to real data.")


@pytest.fixture(scope="module", autouse=True)
def real_data():
    if "tests" in resource_factory.DATA_FOLDER:
        pytest.skip("DATA_FOLDER seems to be a test directory.")
