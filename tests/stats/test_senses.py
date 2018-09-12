import pytest

from acres.stats import senses


def test_print_senses(capsys):
    senses.print_senses("tests/resources/workbench.tsv")

    captured = capsys.readouterr()

    expected = "2\t1"
    actual = captured.out.split("\n")[-2]
    assert expected == actual


def test_print_ambiguous(capsys):
    senses.print_ambiguous("tests/resources/workbench.tsv")

    captured = capsys.readouterr()

    expected = "AP\t['Alkalische Phosphatase', 'Angina pectoris']"
    actual = captured.out.split("\n")[-2]
    assert expected == actual
