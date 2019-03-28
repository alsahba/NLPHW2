from Stemmer import Stemmer
import math

def calculateTotalNumberOfTwoLayerMapping(mapping):
    return sum(count for outerScope in mapping.items() for word, count in outerScope[1].items())


def calculateTotalNumberOfOneLayerMapping(mapping):
    return sum(count for word, count in mapping.items())


def splitWordAndTag(stemmer, word_with_tag):
    separation = word_with_tag.split('/')
    word = stemmer.wordOrganizer(separation[0])
    tag = stemmer.wordOrganizer(separation[1])
    return word, tag


def countEmission(stemmer, emission, words_with_tags):
    for word_with_tag in words_with_tags:
        word = splitWordAndTag(stemmer, word_with_tag)[0]
        if word == 'not a word':
            continue
        tag = splitWordAndTag(stemmer, word_with_tag)[1]

        try:
            emission[tag][word] += 1
        except KeyError:
            try:
                emission[tag][word] = 1
            except KeyError:
                emission[tag] = {word: 1}


def countTransition(stemmer, transition, word_with_tags):
    for i in range(len(words_with_tags) - 1):
        tag = splitWordAndTag(stemmer, words_with_tags[i])[1]
        next_tag = splitWordAndTag(stemmer, words_with_tags[i + 1])[1]

        if tag == 'end' and next_tag == 'start':
            continue

        try:
            transition[tag][next_tag] += 1
        except KeyError:
            try:
                transition[tag][next_tag] = 1
            except KeyError:
                transition[tag] = {next_tag: 1}


def calculateProbability(transition, emission, separated_line):
    mapo = {}
    for i in range(len(separated_line) - 1):
        for m in emission:
            calc = transition.get('start').get(m) / calculateTotalNumberOfOneLayerMapping(transition.get('start'))
            try:
                mapo['start'][m] = calc
            except:
                mapo['start'] = {m: calc}




emission, transition = {}, {}
words_with_tags, lines = [], []
stemmer = Stemmer()

[lines.append('not_a_word/start ' + line + 'not_a_word/end ') for line in open("data.txt", "r").readlines()]
[words_with_tags.append(word.strip()) for line in lines for word in line.split()]

countEmission(stemmer, emission, words_with_tags)
countTransition(stemmer, transition, words_with_tags)

deneme = ["Siz", ",", "sonsuza", "dek", "yürüyeceksiniz", "."]


print(calculateTotalNumberOfTwoLayerMapping(emission))
print(calculateTotalNumberOfTwoLayerMapping(transition))
print(emission.get('start'))
print(transition.get('punc'))

calculateProbability(transition,emission,deneme)
