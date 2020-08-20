import shutil

import pytest

from acres.word2vec import train
from acres.preprocess import resource_factory


@pytest.fixture(scope="module", autouse=True)
def delete_models():
    _delete_contents("tests/models/ngrams")
    _delete_contents("tests/models/word2vec")
    _delete_contents("tests/models/pickle")


def _delete_contents(folder):
    shutil.rmtree(folder, ignore_errors=True)


@pytest.fixture(scope="module", autouse=True)
def path_resource_factory():
    resource_factory.PICKLE_FOLDER = "tests/models/pickle/"
    resource_factory.NGRAMS_FOLDER = "tests/models/ngrams/"
    resource_factory.NN_MODELS_FOLDER = "tests/models/word2vec/"
    resource_factory.DATA_FOLDER = "tests/data"
    resource_factory.reset()
    print("INFO: Switched to test data.")


@pytest.fixture(scope="module", autouse=True)
def word2vec_workers():
    train.WORKERS = 1
    print("INFO: Trying to make word2vec deterministic. Set also PYTHONHASHSEED.")


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
def word_ngrams():
    # Setup: save current one and assign a fake one
    old = resource_factory.WORD_NGRAMS
    resource_factory.WORD_NGRAMS = {"EKG": 500,
                                    "Elektrokardiogramm": 200,
                                    "performed EKG yesterday": 30,
                                    "performed Elektrokardiogramm yesterday": 20,
                                    "performed Eakaga yesterday": 20,
                                    "performed Echokardiogramm 1980": 20,
                                    "scheduled Echokardiogramm yesterday": 20,
                                    "performed Elektro kardiogramm yesterday": 10,  # sic
                                    "performed Effusion yesterday": 5
                                    }
    yield resource_factory.WORD_NGRAMS

    # Teardown: revert back to old
    resource_factory.WORD_NGRAMS = old
