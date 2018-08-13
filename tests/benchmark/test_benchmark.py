from acres.preprocess import resource_factory


def test_fixture():
    assert "tests" not in resource_factory.PICKLE_FOLDER
