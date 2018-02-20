from acres import text_cleanser


def test_find_best_substitution():
    # import pickle
    # normalised_tokens = pickle.load(open("models/pickle/tokens.p", "rb"))

    normalised_tokens = {"Sinus", "rhythmus"}
    candidates = ['123\tSinusrhythmus', '123\tSinusarrhytmie', '123\tkein Sinusrh.']

    actual = text_cleanser.find_best_substitution("SR", candidates, normalised_tokens, "AA")
    expected = ['02\tSinusrhythmus', '00\tSinusarrhytmie']

    assert expected == actual
