def _resolve_ambiguous_lists(lists):
    """

    :param lists:
    :return:
    """
    for a_list in lists:
        list0 = []
        list1 = []
        is_open = True
        is_tuple = False
        for element in a_list:
            if isinstance(element, tuple) and is_open:
                list0.append(element[0])
                list1.append(element[1])
                is_open = False
                is_tuple = True
            else:
                list0.append(element)
                list1.append(element)
        if is_tuple:
            lists.append(list0)
            lists.append(list1)
        else:
            return lists


def _create_string_variants_as_list(a_string, search, replace):
    """
    Analyses a string a_string for all substrings.

    :param a_string:
    :param search:
    :param replace:
    :return: A list constituted by non-substitutable strings and/or search/replace pairs
    """
    if search == "":
        return [a_string]
    ret = []
    i = 0
    built_string = ""
    while True:
        char = a_string[i]
        j = i + len(search)
        if a_string[i:j] == search:
            if built_string != "":
                ret.append(built_string)
            built_string = ""
            ret.append((search, replace))
            i = i + len(search)
        else:
            built_string = built_string + char
            i = i + 1
        if i >= len(a_string):
            if built_string != "":
                ret.append(built_string)
            return ret


def _list_to_string(a_list):
    """
    transforms input of list
    if a list element is not a string: -> empty string

    :param a_list:
    :return:
    """
    out = ""
    for element in a_list:
        if isinstance(element, str):
            out = out + element
        else:
            return ""
    return out


def _list_all_string_variants(a_string, search, replace):
    """

    :param a_string:
    :param search:
    :param replace:
    :return:
    """
    out = []
    a_list = _resolve_ambiguous_lists([_create_string_variants_as_list(a_string, search, replace)])
    for element in a_list:
        a_string = _list_to_string(element)
        if a_string != "":
            out.append(a_string)
    return out


def generate_all_variants_by_rules(raw_string):
    """

    :param raw_string:
    :return:
    """
    rules = [
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

    out = [raw_string]

    for rule in rules:
        for a_string in out:
            new_list = _list_all_string_variants(a_string, rule[0], rule[1])
            for element in new_list:
                if element not in out:
                    out.append(element)
    return out
