# Create file dumps for large ngram resources
# for better performance
# Stefan Schulz 21 August 2017

# XXX all pickle dumps should be created in this module . 


import pickle
import collections

NGRAMSTAT = "..\\..\\stat\corpus_cardio_training_cleaned_1_to_7gram_stat.txt"
# ngram statistics representing a specific document genre and domain


def CreateNormalisedTokenDump():
    # creates a set of all tokens in the ngram table, taking into account all possible variants
    # typical for clinical German
    # XXX Check whether it's used !!
    # INCOMLETE RULESET FOR TRANSFORMING 8 bit to 7 bit
    # including normalizing K-C-Z (only relevant for Medical German)
    # XXX Soundex ?
    # XXX similar function elsewhere?
    allTokens = set() 
    allTokenVariants = set()
    with open(NGRAMSTAT) as f:
        for row in f:
            row = row.replace("-", " ").replace("/", " ").replace("(", " ").replace(")", " ")
            tokens = row.split(" ")
            for token in tokens:
                allTokens.add(token)
        for token in allTokens:          
            token = token.replace(".", "").replace(",", "").replace(";", "").replace(":", "").replace("!", "").replace("?", "")
            allTokenVariants.add(token)
            allTokenVariants.add(token.lower())
            token = token.replace("k", "c").replace("z", "c")
            allTokenVariants.add(token)
            allTokenVariants.add(token.lower())
            token = token.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
            allTokenVariants.add(token)
            allTokenVariants.add(token.lower())
    pickle.dump(allTokenVariants, open("tokens.p", "wb"))
 

def CreateNgramstatDump(nGramStatFile, ngramstat, minFreq):
    # creates dump of ngram and ngram variants
    # create dump of word indices for increasing performance
    with open(nGramStatFile) as f:
        ID = 1
        for row in f:
            if row[8] == "\t" :
                #freq = '{:0>7}'.format(int(row.split("\t")[0]))
                freq = row.split("\t")[0]
                freq = '{:0>7}'.format(int(row.split("\t")[0]))
                ngram = row.split("\t")[1].strip()
                if int(freq) >= minFreq:
                    ngramstat[ID] = freq + "\t" + ngram; ID +=1
                    # adding variations according to specific tokenization
                    # rules dependent on punctuation chars,
                    # guided by obseverations of German clinical language. 
                    if "-" in row:
                        ## !!! GERMAN-DEPENDENT !!!
                        # Variant 1: hyphen may be omitted (non-standard German)
                        # "Belastungs-Dyspnoe" -->  "Belastungs Dyspnoe"
                        ngramstat[ID] = freq + "\t" + ngram.replace("-", " ") ; ID +=1
                        # Variant 2: words may be fused (should also be decapitalised
                        # but this is not relevant due to case-insensitive matching)
                        # "Belastungs-Dyspnoe" -->  "BelastungsDyspnoe"
                        ngramstat[ID] = freq + "\t" + ngram.replace("-", "") ; ID +=1
                    if row[-1] in ".:;,-?!/":
                        # Variant 3: removal of trailing punctuation
                        # End of sentence should not restrain reuse of tokens
                        # E.g. "Colonoskopie."
                        # TO DO: investigate solutions to solve it before creating ngrams
                        # !!! FIX ME: sum up frequencies
                        ngramstat[ID] = freq + "\t" + ngram[:-1]; ID +=1
                    if "/" in row:
                        # Variant 4: insertion of spaces around "/", because
                        # "/" is often used as a token separator with shallow meaning
                        # "/" 
                        ngramstat[ID] = freq + "\t" + ngram.replace("/", " / "); ID +=1
                    if ", " in row:
                        # Variant 5: insertion of space before comma, to make the
                        # preceding token accessible
                        ngramstat[ID] = freq + "\t" + ngram.replace(", ", " , "); ID +=1
                    if "; " in row:
                        # the same with semicolon
                        ngramstat[ID] = freq + "\t" + ngram.replace("; ", " ; "); ID +=1
                    if ": " in row:
                        # the same with colon
                        ngramstat[ID] = freq + "\t" + ngram.replace(": ", " : "); ID +=1

    index = collections.defaultdict(set)
    for ID in ngramstat:
        # inverted index for performance issue when retrieving ngram records
        # XXX Think about trie data structure
        #print(ngramstat[ID])
        ngram = ngramstat[ID].split("\t")[1]
        words = ngram.split(" ")
        for word in words:
             index[word].add(ID)
             if len(word) > 1 and not word[-1].isalpha():
                 index[word[0:-1]].add(ID)
                 
    pickle.dump(ngramstat, open("pickle//ngramstat.p", "wb"))
    pickle.dump(index, open("pickle//index.p", "wb"))

ngramstat = {}
# Create pickle dump for min freq 3 (improve performance)
CreateNgramstatDump(NGRAMSTAT, ngramstat, 3)

1/0


# Load dumps

print("Begin Read Dump")
ngramstat = pickle.load(open("pickle//ngramstat.p", "rb"))
print("-")
index = pickle.load(open("pickle//index.p", "rb"))
print("-")
normalisedTokens = pickle.load(open("pickle//tokens.p", "rb"))
print("End Read Dump")

1 / 0

