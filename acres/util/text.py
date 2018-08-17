import string

from acres.preprocess import resource_factory


def diacritics() -> str:
    """
    TODO ... explain why

    :return: A string of diacritic characters
    """
    return "µÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ"


def fix_line_endings(
        long_text: str,
        line_break_marker="¶",
        char_ngram_length=8,
        line_break_marker_position=3) -> str:
    """
    addresses the problem that many texts come with
           artificial line breaks. These breaks are removed if
           distributional data show that an unbroken continuation of
           the text is more likely than the break
    :param long_text:
    :param line_break_marker:
    :param char_ngram_length:
    :param line_break_marker_position:
    :return:
    """
    char_ngram_dict = resource_factory.get_character_ngrams()

    out = ""
    long_text = long_text.strip().replace("\n", line_break_marker)
    i = 0
    while i + char_ngram_length < len(long_text):
        char = long_text[i]
        ngr = long_text[i:i + char_ngram_length]

        # line break marker at nth position
        if ngr[line_break_marker_position] == line_break_marker:
            ngr_clean = clear_digits(ngr, "Ð")
            ngr_clean_space = ngr_clean.replace(line_break_marker, " ")
            if ngr_clean in char_ngram_dict:
                n_breaks = char_ngram_dict[ngr_clean]
            else:
                n_breaks = 0
            if ngr_clean_space in char_ngram_dict:
                n_spaces = char_ngram_dict[ngr_clean_space]
            else:
                n_spaces = 0
            # logger.debug("----")
            # logger.debug(ngr)
            # logger.debug("With new line: %s", n_breaks)
            # logger.debug("With space: %s", n_spaces)
            if n_spaces > n_breaks:
                # TODO: line_break_marker as delimiter
                # What happens if the break marker symbol also occurs in the original text
                # probably safe: using the "¶" character for line breaks
                # Check for whole code how delimiters are handled and how this
                # might interfere with text processing
                out = out + ngr.replace(line_break_marker, " ")
                i = i + char_ngram_length
                if i >= len(long_text):
                    break
            else:
                out = out + char
                i = i + 1
                if i == len(long_text):
                    break
        else:
            out = out + char
            i = i + 1
            if i == len(long_text):
                break

    out = out + long_text[i:] + line_break_marker
    return out


def clear_digits(str_in: str, substitute_char: str) -> str:
    """
       substitutes all digits by a character (or string)

       Example: ClearDigits("Vitamin B12", "°"):

       :param str_in:
       :param substitute_char:

       """
    out = ""
    for c in str_in:
        if c in "0123456789":
            out = out + substitute_char
        else:
            out = out + c
    return out


def transliterate_to_seven_bit(str_in: str, language="de") -> str:
    """
    Converts string to 7-bit ASCII, considering language - specific rules,
    such as in German "Ä" -> "AE", in English "Ä" -> "A"
    Considering in-built capitalization rules such as "ß" -> "SS"
    TODO: completing transliteration rules when non-Western languages are used
    consider using unidecode
    :param str_in:
    :param language: the language for which rules are defined (ISO_639-1)
    :return:
    """
    substitutions = {
        "À": "A",
        "Á": "A",
        "Â": "A",
        "Ã": "A",
        "Ä": "A",
        "Å": "A",
        "Æ": "AE",
        "Ç": "C",
        "È": "E",
        "É": "E",
        "Ê": "E",
        "Ë": "E",
        "Ì": "I",
        "Í": "I",
        "Î": "I",
        "Ï": "I",
        "Ñ": "N",
        "Ò": "O",
        "Ó": "O",
        "Ô": "O",
        "Õ": "O",
        "Ö": "O",
        "Ø": "O",
        "Ù": "U",
        "Ú": "U",
        "Û": "U",
        "Ü": "U"}

    if language == "de":
        substitutions["Ä"] = "AE"
        substitutions["Å"] = "AA"
        substitutions["Ö"] = "OE"
        substitutions["Ø"] = "OE"
        substitutions["Ü"] = "UE"

    return "".join([substitutions.get(c, c) for c in str_in.upper()])


def substitute_c_and_ph_by_context(str_in, language="de"):
    """
    Applies normalization rules that improves retrieval of
    clinical terms. This function transforms an English / Latin spelling
    pattern by a German one
    Also maps to 7bit chars

    :param str_in:
    :param language: the language for which rules are defined (ISO_639-1)
    :return:
    """
    # no Acronym
    if language == "de":
        if len(str_in) == 1:
            return str_in.isupper()
        if len(str_in) == 2 and str_in[1].isupper():
            return str_in
        if str_in[2].isupper():
            return str_in
        str_in = transliterate_to_seven_bit(str_in)
        return str_in.replace("CAE", "ZAE").replace("COE", "ZOE"). \
            replace("CA", "KA").replace("CO", "KO"). \
            replace("CU", "KU").replace("CE", "ZE").replace("CI", "ZI"). \
            replace("CY", "ZY").replace("PH", "F")


def substitute_k_and_f_and_z_by_context(str_in, language="de"):
    """
    Applies normalization rules that improves retrieval of
    clinical terms. This function transforms a German spelling
    pattern by a English / Latin one.
    Also maps to 7bit chars and upper case everything.
    Input should be a single token.

    @todo Enforce it's a single token

    :param str_in:
    :param language: the language for which rules are defined (ISO_639-1)
    :return:
    """
    # no Acronym
    if language == "de":
        if len(str_in) == 1:
            return str_in.upper()

        # Check for acronym
        # TODO Use is_acronym
        if len(str_in) == 2 and str_in[1].isupper():
            return str_in
        if str_in[2].isupper():
            return str_in

        str_in = transliterate_to_seven_bit(str_in)
        return str_in.replace("ZAE", "CAE").replace("ZOE", "COE"). \
            replace("ZI", "CI").replace("ZE", "CE"). \
            replace("KA", "CA").replace("KO", "CO").replace("KU", "CU"). \
            replace("ZY", "CY").replace("F", "PH")


def simplify_german_string(str_in_german: str) -> str:
    """
    Decapitalises, substitutes umlauts, sharp s and converts k and z to c

    TODO ... explain why

    :param str_in_german:
    :return:
    """
    str_in_german = str_in_german.lower()
    str_in_german = str_in_german.replace(
        "k", "c").replace("z", "c").replace("ß", "ss")
    str_in_german = str_in_german.replace("é", "e").replace("à", "a")
    return str_in_german.replace("ä", "ae").replace(
        "ö", "oe").replace("ü", "ue")


def reduce_repeated_chars(str_in, char, n):
    """
    :param str_in: text to be cleaned
    :param char: character that should not occur more than n times in sequence
    :param remaining_chars: n
    :return:
    """
    prev = ""
    cnt = 0
    out = ""
    for c in str_in:
        if c == char:
            cnt += 1
            if cnt <= n:
                out = out + c

        else:
            cnt = 0
            out = out + c
    return out


def replace_punctuation(s):
    _punctuation = set(string.punctuation)
    for punct in set(s).intersection(_punctuation):
        s = s.replace(punct, ' ')
    return ' '.join(s.split())


rules = [("pha", "fa"), ("fa", "pha"), ("Pha", "Fa"), ("Fa", "Pha"),
         ("phe", "fe"), ("fe", "phe"), ("Phe", "Fe"), ("Fe", "Phe"),
         ("phi", "fi"), ("fi", "phi"), ("Phi", "Fi"), ("Fi", "Phi"),
         ("pho", "fo"), ("fo", "pho"), ("Pho", "Fo"), ("Fo", "Pho"),
         ("phu", "fu"), ("fu", "phu"), ("Phu", "Fu"), ("Fu", "Phu"),
         ("phy", "fy"), ("fy", "phy"), ("Phy", "Fy"), ("Fy", "Phy"),
         ("phä", "fä"), ("fä", "phä"), ("Phä", "Fä"), ("Fä", "Phä"),
         ("phö", "fö"), ("fö", "phö"), ("Phö", "Fö"), ("Fö", "Phö"),
         ("phü", "fü"), ("fü", "phü"), ("Phü", "Fü"), ("Fü", "Phü"),
         ("ka", "ca"), ("ca", "ka"), ("Ka", "Ca"), ("Ca", "Ka"),
         ("ko", "co"), ("co", "ko"), ("Ko", "Co"), ("Co", "Ko"),
         ("ku", "cu"), ("cu", "ku"), ("Ku", "Cu"), ("Cu", "Ku"),
         ("cy", "zy"), ("zy", "cy"), ("Cy", "Zy"), ("Zy", "Cy"),
         ("ci", "zi"), ("zi", "ci"), ("Ci", "Zi"), ("Zi", "Ci"),
         ("ce", "ze"), ("ze", "ce"), ("Ce", "Ze"), ("Ze", "Ce"),
         ("cl", "kl"), ("kl", "cl"), ("Cl", "Kl"), ("Kl", "Cl"),
         ("cr", "kr"), ("kr", "cr"), ("Cr", "Kr"), ("Kr", "Cr"),
         ("cn", "kn"), ("kn", "cn"), ("Cn", "Kn"), ("Kn", "Cn"),
         ("cc", "kz"), ("kz", "cc"),
         ("ö", "oe"), ("Ö", "Oe"),
         ("ü", "ue"), ("Ü", "Ue"),
         ("ä", "ae"), ("Ä", "Ae"),
         ("ß", "ss"),
         ("é", "e")]


def resolve_ambiguous_lists(LL):
    for L in LL:
        L0 = []
        L1 = []
        Open = True
        Tuple = False
        for e in L:
            if type(e) is tuple and Open == True:
                L0.append(e[0])
                L1.append(e[1])
                Open = False
                Tuple = True
            else:
                L0.append(e)
                L1.append(e)
        if Tuple == True:
            LL.append(L0)
            LL.append(L1)
        else:
            return LL


def create_string_variants_as_list(st, se, re):
    # analyses a string st for all substrings
    # returns a list constituted by
    # non-substitutable strings and/or
    # search / replace pairs
    if se == "": return [st]
    r = []
    u = len(st) - len(se)
    i = 0
    s = ""
    while True:
        c = st[i]
        j = i + len(se)
        if st[i:j] == se:
            if s != "": r.append(s)
            s = ""
            r.append((se, re))
            i = i + len(se)
        else:
            s = s + c
            i = i + 1
        if i >= len(st):
            if s != "": r.append(s)
            return r


def list_to_string(lst):
    # transforms input of list
    # if a list element is not a string: -> empty string
    out = ""
    for e in lst:
        if type(e) is str:
            out = out + e
        else:
            return ""
    return out


# print(list_to_string(["a", "b" , "c", ("g", "e")]))


def list_all_string_variants(st, se, re):
    outL = []
    L = resolve_ambiguous_lists([create_string_variants_as_list(st, se, re)])
    for e in L:
        s = list_to_string(e)
        if s != "":
            outL.append(s)
    return outL


# print(list_all_string_variants("cyclophosphamid", "id", "ide"))

# 1 / 0

def generate_all_variants_by_rules(st):
    lstRules = [
        ("krankheit", " Disorder"),
        ("fa", "pha"), ("Fa", "Pha"),
        ("fe", "phe"), ("Fe", "Phe"),
        ("fi", "phi"), ("Fi", "Phi"),
        ("fo", "pho"), ("Fo", "Pho"),
        ("fu", "phu"), ("Fu", "Phu"),
        ("fy", "phy"), ("Fy", "Phy"),
        ("fä", "phä"), ("Fä", "Phä"),
        ("fö", "phö"), ("Fö", "Phö"),
        ("fü", "phü"), ("Fü", "Phü"),
        ("ka", "ca"), ("Ka", "Ca"),
        ("ko", "co"), ("Ko", "Co"),
        ("ku", "cu"), ("Ku", "Cu"),
        ("zy", "cy"), ("Zy", "Cy"),
        ("zi", "ci"), ("Zi", "Ci"),
        ("ze", "ce"), ("Ze", "Ce"),
        ("kl", "cl"), ("Kl", "Cl"),
        ("kr", "cr"), ("Kr", "Cr"),
        ("kn", "cn"), ("Kn", "Cn"),
        ("kz", "cc"),
        ("ö", "e"), ("Ö", "E"),  # because of esophagus
        ("ü", "ue"), ("Ü", "Ue"),
        ("ä", "ae"), ("Ä", "Ae")]

    outL = [st]

    for r in lstRules:
        # print(r)
        for s in outL:
            newL = []
            newL = list_all_string_variants(s, r[0], r[1])
            for e in newL:
                if not e in outL: outL.append(e)
    return (outL)
