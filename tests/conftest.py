import pytest, os

from acres.preprocess import resource_factory


@pytest.fixture(scope="module", autouse=True)
def delete_models():
    _delete_contents("tests/models/log")
    _delete_contents("tests/models/ngrams")
    _delete_contents("tests/models/nn")
    _delete_contents("tests/models/pickle")


def _delete_contents(folder):
    for file in os.listdir(folder):
        if file == "empty":
            continue
        filename = os.path.join(folder, file)
        os.unlink(filename)


@pytest.fixture(scope="module", autouse=True)
def path_resource_factory():
    resource_factory.PICKLE_FOLDER = "tests/models/pickle/"
    resource_factory.NGRAMS_FOLDER = "tests/models/ngrams/"
    resource_factory.LOG_FOLDER = "tests/models/log/"
    resource_factory.NN_MODELS_FOLDER = "tests/models/nn/"
    resource_factory.DATA_FOLDER = "tests/data"
    resource_factory.reset()
    print("INFO: Switched to test data.")


@pytest.fixture(scope="module")
def ngramstat():
    # Setup: save current one and assign a fake one
    old = resource_factory.NGRAMSTAT
    resource_factory.NGRAMSTAT = {1: (2000, "¶"),
                                  2: (200, "der"),
                                  3: (50, "EKG"),
                                  4: (27, "* EKG ¶"),
                                  5: (20, "Im EKG"),
                                  6: (19, "* Physikalischer Status ¶"),
                                  7: (19, "for WORD embeddings"),
                                  8: (20, "for WabcOabcRabcDabc embeddings"),
                                  }
    yield resource_factory.NGRAMSTAT

    # Teardown: revert back to old
    resource_factory.NGRAMSTAT = old


@pytest.fixture(scope="module")
def index():
    # Setup: save current one and assign a fake one
    old = resource_factory.INDEX
    resource_factory.INDEX = {"¶": {1, 4, 6},
                              "der": {2},
                              "EKG": {3, 4, 5},
                              "*": {4, 6},
                              "Im": {5},
                              "Physikalischer": {6},
                              "Status": {6},
                              "for": {7, 8},
                              "WORD": {7},
                              "embeddings": {7, 8},
                              "WabcOabcRabcDabc": {8}
                              }
    yield resource_factory.INDEX

    # Teardown: revert back to old
    resource_factory.INDEX = old