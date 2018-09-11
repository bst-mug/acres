from typing import List

from acres.util import acronym
from acres.util import functions


class Stats:
    """
    Class that generates and holds stats about a given text.
    """

    line_separator = "\n"

    def __init__(self, chars: int = 0, types: int = 0, tokens: int = 0, acronym_types: int = 0,
                 acronyms: int = 0, sentences: int = 0):
        self.chars = chars
        self.types = types
        self.tokens = tokens
        self.acronym_types = acronym_types
        self.acronyms = acronyms
        self.sentences = sentences

    def calc_stats(self, text: str):
        self.chars = Stats.count_chars(text)
        self.types = Stats.count_types(text)
        self.tokens = Stats.count_tokens(text)
        self.acronym_types = Stats.count_acronyms_types(text)
        self.acronyms = Stats.count_acronyms(text)
        self.sentences = Stats.count_sentences(text)

    def count_chars(text: str) -> int:
        return len(''.join(text.split()))

    def count_types(text: str) -> int:
        types = set()
        for token in text.split():
            types.add(token)
        return len(types)

    def count_tokens(text: str) -> int:
        return len(text.split())

    def count_acronyms(text: str) -> int:
        return len(Stats._get_acronyms(text))

    def count_acronyms_types(text: str) -> int:
        return len(set(Stats._get_acronyms(text)))

    def count_sentences(text: str) -> int:
        count = 0
        for _ in text.split(Stats.line_separator):
            count += 1
        return count

    def _get_acronyms(text: str) -> List[str]:
        acronyms = []
        for token in text.split():
            if acronym.is_acronym(token):
                acronyms.append(token)
        return acronyms

    def __str__(self):
        ret = []
        ret.append("Chars: " + str(self.chars) + "\n")
        ret.append("Types: " + str(self.types) + "\n")
        ret.append("Tokens: " + str(self.tokens) + "\n")
        ret.append("Acronym Types: " + str(self.acronym_types) + "\n")
        ret.append("Acronyms: " + str(self.acronyms) + "\n")
        ret.append("Sentences: " + str(self.sentences) + "\n")
        return ''.join(ret)

    def __add__(self, other):
        self.chars += other.chars
        self.types += other.types
        self.tokens += other.tokens
        self.acronym_types += other.acronym_types
        self.acronyms += other.acronyms
        self.sentences += other.sentences
        return self

    def __radd__(self, other):
        return self.__add__(other)


def get_stats(corpus_path: str) -> List[Stats]:
    texts = functions.robust_text_import_from_dir(corpus_path)

    full_text = Stats.line_separator.join(texts)
    texts.append(full_text)

    ret = []
    for text in texts:
        stats = Stats()
        stats.calc_stats(text)
        ret.append(stats)
    return ret


def print_stats() -> None:
    all_stats = get_stats(functions.import_conf("CORPUS_PATH"))
    [print(doc) for doc in all_stats]
    print("Total docs: " + str(len(all_stats) - 1))


if __name__ == "__main__":
    print_stats()
