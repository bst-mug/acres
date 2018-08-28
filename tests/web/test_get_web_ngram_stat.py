def test_get_best_acronym_web_resolution():
    pass
    #assert ("Elektrokardiogramm", 2) == rater.get_best_acronym_web_resolution("", "EKG","Absolute Arrhythmie", 3, 5)


def test_ngrams_web_dump():
    pass

    """
    # FIXME Flaky test in different geographic regions
     
    # A bing query for "EKG" should retrieve a high frequency of the word "Elektrokardiogramm!

    acronym = "EKG"
    hit = False
    lst_result = get_web_ngram_stat.ngrams_web_dump("http://www.bing.de/search?cc=de&q=%22" + acronym + "%22", 1, 10)
    for i in range(1, 30):
        (freq, exp) = lst_result[i]
        if "Elektrokardiogram" in exp:
            hit = True
    assert hit
    """
