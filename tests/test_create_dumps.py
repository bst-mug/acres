import os.path

from acres import create_dumps


def test_create_morpho_dump():
    output_file = "models/pickle/morphemes.p"

    os.remove(output_file)
    assert not os.path.isfile(output_file)

    create_dumps.create_morpho_dump()
    assert os.path.isfile(output_file)
