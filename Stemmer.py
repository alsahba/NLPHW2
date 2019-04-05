from TurkishStemmer import TurkishStemmer

class Stemmer(object):

    stemmer = TurkishStemmer()
    def __init__(self):
        pass

    def wordOrganizer(self, word):
        word = word.replace("_", " ")
        if '\'' in word:
            n = word[0:int(word.find('\''))]
            # n = self.stemmer.stem(n)
            return n.lower()
        # word = self.stemmer.stem(word)
        return word.lower()
