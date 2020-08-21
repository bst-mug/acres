"""
Module with general functions.
"""
import logging
import os
import random
from configparser import ConfigParser
from typing import Dict, List, Optional, Tuple, Iterable

from acres import constants

logger = logging.getLogger(__name__)


def import_conf(key: str) -> Optional[str]:
    """

    :param key:
    :return:
    """
    config = ConfigParser(os.environ)
    config.read("config.ini")
    if key not in config['DEFAULT']:
        logging.critical("'%s' was not found in the DEFAULT section of config.ini.", key)
        return None
    return config['DEFAULT'][key]


def create_ngram_statistics(input_string: str, n_min: int, n_max: int) -> Dict[str, int]:
    """
    Creates a dictionary that counts each nGram in an input string. Delimiters are spaces.

    Example: bigrams and trigrams
    nMin = 2 ,   nMax = 3
    PROBE: # print(WordNgramStat('a ab aa a a a ba ddd', 1, 4))

    :param input_string:
    :param n_min:
    :param n_max:
    :return:
    """
    logger.info("Creating ngram statistics...")

    output = {}  # type: Dict[str, int]
    lines = input_string.splitlines()
    for line in lines:
        if line == '':
            continue
        # TODO does it ever happen? splitlines should have taken care already...
        line = line.replace('\r', ' ')
        line = line.replace('\n', ' ')
        line = line.replace('  ', ' ')
        line = line.strip()
        #print(line)
        cleaned_line = line.split(" ")
        for i in range(n_min, n_max + 1):
            for j in range(len(cleaned_line) - i + 1):
                ngram = ' '.join(cleaned_line[j:j + i])
                output.setdefault(ngram, 0)
                output[ngram] += 1
    #    Example for formatted output, sorted, reverse order
    #    for w in sorted(output, key=output.get, reverse = True):
    #       print ('{:>8}'.format(output[w]) + '\t' + w)
    return output


def is_stopword(str_in: str) -> bool:
    """
    Tests whether word is stopword, according to list.

    For German, source http://snowball.tartarus.org/algorithms/german/stop.txt

    :param str_in:
    :return:
    """
    ret = False
    if constants.LANGUAGE == "de":
        stopwords = {'ab', 'aber', 'alle', 'allem', 'allen', 'aller', 'alles', 'als', 'also', 'am',
                     'an', 'andere', 'anderem', 'anderem', 'anderen', 'anderer', 'anderer',
                     'anderes', 'andern', 'anders', 'auch', 'auf', 'aus', 'bei', 'bin', 'bis',
                     'bist', 'da', 'damit', 'dann', 'das', 'dass', 'daß', 'dasselbe', 'dazu',
                     'dein', 'deine', 'deinem', 'deinen', 'deiner', 'deines', 'dem', 'demselben',
                     'den', 'denn', 'denselben', 'der', 'derer', 'derselbe', 'derselben', 'des',
                     'desselben', 'dessen', 'dich', 'die', 'dies', 'diese', 'dieselbe', 'dieselben',
                     'diesem', 'diesen', 'dieser', 'dieses', 'dir', 'doch', 'dort', 'du', 'durch',
                     'ein', 'eine', 'einem', 'einen', 'einer', 'eines', 'einig', 'einige',
                     'einigem', 'einigen', 'einiger', 'einiges', 'einmal', 'er', 'es', 'etwas',
                     'euch', 'euer', 'eure', 'eurem', 'euren', 'eurer', 'eures', 'für', 'gegen',
                     'gewesen', 'hab', 'habe', 'haben', 'hat', 'hatte', 'hatten', 'hier', 'hin',
                     'hinter', 'ich', 'ihm', 'ihn', 'ihnen', 'ihr', 'ihre', 'ihrem', 'ihren',
                     'ihrer', 'ihres', 'im', 'in', 'indem', 'ins', 'ist', 'jede', 'jedem', 'jeden',
                     'jeder', 'jedes', 'jene', 'jenem', 'jenen', 'jener', 'jenes', 'jetzt', 'kann',
                     'kein', 'keine', 'keinem', 'keinen', 'keiner', 'keines', 'können', 'könnte',
                     'machen', 'man', 'manche', 'manchem', 'manchen', 'mancher', 'manches', 'mein',
                     'meine', 'meinem', 'meinen', 'meiner', 'meines', 'mich', 'mir', 'mit', 'muss',
                     'musste', 'nach', 'nicht', 'nichts', 'noch', 'nun', 'nur', 'ob', 'oder',
                     'ohne', 'sehr', 'sein', 'seine', 'seinem', 'seinen', 'seiner', 'seines',
                     'selbst', 'sich', 'sie', 'sind', 'so', 'solche', 'solchem', 'solchen',
                     'solcher', 'solches', 'soll', 'sollte', 'sondern', 'sonst', 'über', 'um',
                     'und', 'uns', 'unser', 'unsere', 'unserem', 'unseren', 'unseres', 'unter',
                     'viel', 'vom', 'von', 'vor', 'während', 'war', 'waren', 'warst', 'was', 'weg',
                     'weil', 'weiter', 'welche', 'welchem', 'welchen', 'welcher', 'welches', 'wenn',
                     'werde', 'werden', 'wie', 'wieder', 'will', 'wir', 'wird', 'wirst', 'wo',
                     'wollen', 'wollte', 'würde', 'würden', 'zu', 'zum', 'zur', 'zwar', 'zwischen'}
        if str_in.lower() in stopwords:
            ret = True
    return ret


def robust_text_import_from_dir(path: str) -> List[str]:
    """
    Read the content of valid text files from a path into a list of strings.

    :param path: The path to look for documents.
    :return: A list of strings containing the content of each valid file.
    """
    logger.info("Loading documents from %s...", path)

    texts = []
    # print(path)
    files = os.listdir(path)

    for filename in files:
        try:
            with open(path + "/" + filename, "r", encoding="utf-8") as file:
                content = file.read()
                texts.append(content)
                # print(file + " " + str(len(content)))
        except UnicodeDecodeError:
            logger.warning("Corrupt file: %s", filename)
            continue
        except IOError as ex:
            logger.warning("I/O error (%d) while reading %s: %s", ex.errno, filename, ex.strerror)
            continue

    return texts


def partition(word: str, partitions: int) -> int:
    """
    Find a bucket for a given word.

    :param word:
    :param partitions:
    :return:
    """
    a = ord('a')
    z = ord('z')
    value = ord(word[0].lower())
    if partitions > 1 and a <= value <= z:
        pos = value - a
        return int(pos * (partitions - 1) / (z - a + 1)) + 1

    # Catch-all for numbers, symbols and diacritics.
    return 0


def sample(iterable: Iterable, chance: float) -> Iterable:
    """
    Randomly sample items from an iterable with a given chance.

    :param iterable:
    :param chance:
    :return:
    """
    # Keep lists deterministic
    random.seed(42)

    for item in iterable:
        if random.random() < chance:
            yield item
