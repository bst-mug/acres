"""
Module for calculating corpus statistics.
"""
from typing import List

from acres.util import acronym
from acres.util import functions


class Stats:
    """
    Class that generates and holds stats about a given text.
    """

    line_separator = "\n"

    def __init__(self) -> None:
        self.chars = 0
        self.types = 0
        self.tokens = 0
        self.acronym_types = 0
        self.acronyms = 0
        self.sentences = 0

    def calc_stats(self, text: str) -> None:
        """
        Calculates statistics for a given text string and sets the results as variables.

        :param text:
        :return:
        """
        self.chars = Stats.count_chars(text)
        self.types = Stats.count_types(text)
        self.tokens = Stats.count_tokens(text)
        self.acronym_types = Stats.count_acronyms_types(text)
        self.acronyms = Stats.count_acronyms(text)
        self.sentences = Stats.count_sentences(text)

    @staticmethod
    def count_chars(text: str) -> int:
        """
        Count the number of non-whitespace chars in a string.

        :param text:
        :return:
        """
        return len(''.join(text.split()))

    @staticmethod
    def count_types(text: str) -> int:
        """
        Count the number of unique tokens (types) in a string.

        :param text:
        :return:
        """
        types = set()
        for token in text.split():
            types.add(token)
        return len(types)

    @staticmethod
    def count_tokens(text: str) -> int:
        """
        Count the number of all tokens in a string.

        :param text:
        :return:
        """
        return len(text.split())

    @staticmethod
    def count_acronyms(text: str) -> int:
        """
        Count the number of acronyms in a string.

        Acronyms are as defined by the `acronym.is_acronym()` function.

        :param text:
        :return:
        """
        return len(Stats._get_acronyms(text))

    @staticmethod
    def count_acronyms_types(text: str) -> int:
        """
        Count the number of unique acronyms in a string.

        Acronyms are as defined by the `acronym.is_acronym()` function.

        :param text:
        :return:
        """
        return len(set(Stats._get_acronyms(text)))

    @staticmethod
    def count_sentences(text: str) -> int:
        """
        Count the number of sentences in a string.

        Sentences are any string separated by `line_separator`.

        :param text:
        :return:
        """
        count = 0
        for _ in text.split(Stats.line_separator):
            count += 1
        return count

    @staticmethod
    def _get_acronyms(text: str) -> List[str]:
        acronyms = []
        for token in text.split():
            if acronym.is_acronym(token):
                acronyms.append(token)
        return acronyms

    def __str__(self) -> str:
        ret = []
        ret.append("Chars: " + str(self.chars) + "\n")
        ret.append("Types: " + str(self.types) + "\n")
        ret.append("Tokens: " + str(self.tokens) + "\n")
        ret.append("Acronym Types: " + str(self.acronym_types) + "\n")
        ret.append("Acronyms: " + str(self.acronyms) + "\n")
        ret.append("Sentences: " + str(self.sentences) + "\n")
        return ''.join(ret)

    def __add__(self, other: 'Stats') -> 'Stats':
        self.chars += other.chars
        self.types += other.types
        self.tokens += other.tokens
        self.acronym_types += other.acronym_types
        self.acronyms += other.acronyms
        self.sentences += other.sentences
        return self

    def __radd__(self, other: 'Stats') -> 'Stats':
        return self.__add__(other)


def get_stats(corpus_path: str) -> List[Stats]:
    """
    Generates all statistics from a given corpus directory.

    :param corpus_path: A list of statistics objects, one for each file found in the corpus dir.
    :return:
    """
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
    """
    Generates and print statistics from the default corpus set in confi.

    :return: None
    """
    corpus_path = functions.import_conf("CORPUS_PATH")
    if not corpus_path:
        return None

    all_stats = get_stats(corpus_path)
    for doc in all_stats:
        print(doc)
    print("Total docs: " + str(len(all_stats) - 1))
    return None


if __name__ == "__main__":
    print_stats()
