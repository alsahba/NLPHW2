class Stemmer(object):

    def __init__(self):
        pass

    def wordOrganizer(self, word):
        word = word.replace("_", " ")
        if '\'' in word:
            n = word[0:int(word.find('\''))]
            return n.lower()
        return word.lower()
