import pytest

from acres.preprocess import resource_factory
from acres.util import functions


@pytest.fixture(scope="module", autouse=True)
def path_resource_factory():
    resource_factory.PICKLE_FOLDER = "models/pickle/"
    resource_factory.NGRAMS_FOLDER = "models/ngrams/"
    resource_factory.LOG_FOLDER = "models/log/"
    resource_factory.NN_MODELS_FOLDER = "models/nn/"
    print("WARNING: Switched to models containing real data.")


@pytest.fixture(scope="module", autouse=True)
def real_data():
    corpus_path = functions.import_conf("CORPUS_PATH")
    if "tests" in corpus_path:
        pytest.skip("CORPUS_PATH seems to be a test directory.")
