"""
Helper functions to calculate evaluation metrics.
"""


def calculate_precision(total_correct: int, total_found: int) -> float:
    """
    Calculate precision as the ratio of correct acronyms to the found acronyms.

    :param total_correct:
    :param total_found:
    :return:
    """
    return total_correct / total_found if total_found != 0 else 0


def calculate_recall(total_correct: int, total_acronyms: int) -> float:
    """
    Calculate reall as the ratio of correct acronyms to all acronyms.

    :param total_correct:
    :param total_acronyms:
    :return:
    """
    return total_correct / total_acronyms if total_acronyms != 0 else 0


def calculate_f1(precision: float, recall: float) -> float:
    """
    Calculates the F1-score.

    :param precision:
    :param recall:
    :return:
    """
    return (2 * precision * recall) / (precision + recall) if (precision + recall) != 0 else 0
