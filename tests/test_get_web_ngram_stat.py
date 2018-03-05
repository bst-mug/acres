from acres import get_web_ngram_stat

def test_dummy():
    assert True

def test_ngrams_web_dump():
    pass

    """
    # FIXME Flaky test in different geographic regions
     
    # A bing query for "EKG" should retrieve a high frequency of the word "Elektrokardiogramm!

    acronym = "EKG"
    hit = False
    lst_result = get_web_ngram_stat.ngrams_web_dump("http://www.bing.de/search?cc=de&q=%22" + acronym + "%22", 1, 10)
    for i in range(1, 30):
        if "Elektrokardiogram" in lst_result[i]:
            hit = True
    assert hit
    """

