import pytest

from acres.stats import stats
from acres.util import functions


def test_get_stats():
    actual = stats.get_stats("tests/data")
    assert len(actual) == 21

    assert actual[20].chars == 147591
    assert actual[20].types == 6427
    assert actual[20].tokens == 21175
    assert actual[20].acronym_types == 443
    assert actual[20].acronyms == 1397
    assert actual[20].sentences == 4970


@pytest.mark.skipif(functions.import_conf("CORPUS_PATH") != "tests/data",
                    reason="Not using test data")
def test_print_stats(capsys):
    stats.print_stats()

    # Capture standard output to test
    # Note that we depend on pytest>=3.7.3 to use it properly
    # (see https://github.com/pytest-dev/pytest/issues/3819)
    captured = capsys.readouterr()
    output_lines = captured.out.split("\n")
    assert output_lines[-2] == "Total docs: 20"
