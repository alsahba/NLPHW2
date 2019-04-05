import math, time
import numpy as np

from Stemmer import Stemmer


def calculateTotalItems(mapping):
    return sum(count for word, count in mapping.items())


def splitWordAndTag(stemmer, word_with_tag):
    separation = word_with_tag.split('/')
    word = stemmer.wordOrganizer(separation[0])
    tag = separation[1].lower()
    return word, tag


def countEmission(stemmer, emission, emission_reversed, words_with_tags):
    for word_with_tag in words_with_tags:
        word, tag = splitWordAndTag(stemmer, word_with_tag)

        if word == 'not a word':
            continue
        addDictionaryToMap(emission, tag, word)
        addDictionaryToMap(emission_reversed, word, tag)


def countTransition(stemmer, transition, word_with_tags):
    for i in range(len(words_with_tags) - 1):
        tag = splitWordAndTag(stemmer, words_with_tags[i])[1]
        next_tag = splitWordAndTag(stemmer, words_with_tags[i + 1])[1]

        if tag == 'end' and next_tag == 'start':
            continue
        addDictionaryToMap(transition, tag, next_tag)


def findMaxProbabilityAndConvertToTuple(mapping):
    maxi, temp_tuple = 0, ()
    for outer_dict in mapping.items():
        for inner_dict in outer_dict[1].items():
            if maxi <= inner_dict[1]:
                maxi = inner_dict[1]
                temp_tuple = (inner_dict[1], inner_dict[0])
    return temp_tuple

#
def findMaxProbabilityForLastWord(mapping):
    max_probability, temp_tuple = 0, ()
    [map(max_probability, inner_dict[1]) and map(temp_tuple, (inner_dict[1], outer_dict[0])) for outer_dict in mapping.items() for inner_dict in outer_dict[1].items()]
    return temp_tuple
#

def convertDictToTuple(mapping):
    return [innerDict for innerDict in mapping.items()][0]


def tracePath(stemmer, separated_line, mapping):
    trace = []
    sizeOfLine = len(separated_line)
    prev_tag = convertDictToTuple(mapping.get('not a word').get('end'))[0]

    for i in reversed(range(sizeOfLine)):
        word = splitWordAndTag(stemmer, separated_line[i])[0]
        trace.append(prev_tag)
        prev_tag = convertDictToTuple(mapping.get(word).get(prev_tag))[0]
    return trace


def tracePathNew(stemmer, separated_line, array):
    trace = []
    sizeOfLine = len(separated_line)
    prev_tag = array[sizeOfLine].get('end')[0]

    for i in reversed(range(sizeOfLine)):
        word = splitWordAndTag(stemmer, separated_line[i])[0]
        trace.append(prev_tag)
        prev_tag = array[i].get(prev_tag)[0]
    return trace


def calculateTransitionProbability(transition, tag, prev_tag):
    denominator = calculateTotalItems(transition.get(prev_tag)) + len(transition.get(prev_tag))
    try:
        transition_probability = (transition.get(prev_tag).get(tag)) / denominator
    except:
        transition_probability =  0
    return transition_probability


def calculateEmissionProbability(emission, tag, word):
    denominator = calculateTotalItems(emission.get(tag))
    try:
        emission_probability = (emission.get(tag).get(word)) / denominator
    except:
        emission_probability = 0
    return emission_probability


def findFirstTransitionProbabilities(stemmer, emission, transition, separated_line, word_probability_mapping):
    word = splitWordAndTag(stemmer, separated_line[0])[0]
    for tag in emission:
        transition_probability = calculateTransitionProbability(transition, tag, 'start')
        emission_probability = calculateEmissionProbability(emission, tag, word)
        addDictionaryToMap(word_probability_mapping, word, tag, 'start', transition_probability * emission_probability)


#todo asdgsadg
def findFirstTransitionProbabilityNew(stemmer, emission, emission_reversed, transition, separated_line, word_probability_array):
    word = splitWordAndTag(stemmer, separated_line[0])[0]
    for tag in emission:
        transition_probability = calculateTransitionProbability(transition, tag, 'start')
        emission_probability = calculateEmissionProbability(emission, tag, word)
        calculated_probability = transition_probability * emission_probability
        if emission_reversed.get(word) is None:
            calculated_probability = transition_probability
        try:
            word_probability_array[0][tag] = ('start', calculated_probability)
        except:
            word_probability_array[0] = {tag: ('start', calculated_probability)}



def findLastTransitionProbabilities(transition, prev_word, word_probability_mapping):
    max_probability = 0
    for tag in transition:
        if tag == 'start':
            continue

        transition_probability = calculateTransitionProbability(transition, 'end', tag)
        probability_prev_tag_tuple = convertDictToTuple(word_probability_mapping.get(prev_word).get(tag))
        calculated_probability = probability_prev_tag_tuple[1] * transition_probability

        if max_probability <= calculated_probability:
            max_probability = calculated_probability
            addDictionaryToMap(word_probability_mapping, 'not a word', 'end', tag, calculated_probability)


def findLastTransitionProbabilityNew(transition, prev_word, word_probability_array, index):
    max_probability = 0
    for tag in transition:
        if tag == 'start':
            continue

        transition_probability = calculateTransitionProbability(transition, 'end', tag)
        probability_tuple = word_probability_array[index].get(tag)
        calculated_probability = probability_tuple[1] * transition_probability

        if max_probability <= calculated_probability:
            max_probability = calculated_probability
            try:
                word_probability_array[index + 1]['end'] = (tag, calculated_probability)
            except:
                word_probability_array[index + 1] = {'end': (tag, calculated_probability)}


def addDictionaryToMap(mapping, tag, tag_word, probability=None, prev_tag=None):
    if probability is None and prev_tag is None:
        try:
            mapping[tag][tag_word] += 1
        except KeyError:
            try:
                mapping[tag][tag_word] = 1
            except KeyError:
                mapping[tag] = {tag_word: 1}
    else:
        try:
            mapping[tag][tag_word] = {probability: prev_tag}
        except KeyError:
            mapping[tag] = {tag_word: {probability: prev_tag}}


def compareResults(stemmer, separated_line, result_list):
    correct_result = sum([1 for index, word_with_tag in enumerate(separated_line) if splitWordAndTag(stemmer, word_with_tag)[1] == result_list[index]])
    return (correct_result, len(separated_line))


def viterbiNew(stemmer, transition, emission, emission_reversed, separated_line):
    word_probability_array = np.empty(len(separated_line) + 1, dtype=dict)
    findFirstTransitionProbabilityNew(stemmer, emission, emission_reversed, transition, separated_line, word_probability_array)

    for i in range(len(separated_line) - 1):
        prev_word = splitWordAndTag(stemmer, separated_line[i])[0]
        word = splitWordAndTag(stemmer, separated_line[i + 1])[0]

        for tag in emission:
            emission_probability = calculateEmissionProbability(emission, tag, word)
            temp_mapping = {}

            for prev_probabilities in word_probability_array[i].items():
                prev_tag, prev_probability = prev_probabilities
                transition_probability = calculateTransitionProbability(transition, tag, prev_tag)
                calculated_probability = prev_probability[1] * transition_probability * emission_probability
                if emission_probability == 0 and emission_reversed.get(word) is None:
                    calculated_probability = prev_probability[1] * transition_probability

                try:
                        temp_mapping[tag][prev_tag] = calculated_probability
                except:
                        temp_mapping[tag] = {prev_tag: calculated_probability}

            max_probability, prev_tag = findMaxProbabilityAndConvertToTuple(temp_mapping)
            try:
                word_probability_array[i+1][tag] = (prev_tag, max_probability)
            except:
                word_probability_array[i+1] = {tag: (prev_tag, max_probability)}


    findLastTransitionProbabilityNew(transition, splitWordAndTag(stemmer, separated_line[-1])[0], word_probability_array, i + 1)
    result_list = tracePathNew(stemmer, separated_line, word_probability_array)
    return compareResults(stemmer, separated_line, result_list[::-1])



def viterbi(stemmer, transition, emission, separated_line):
    word_probability_mapping = {}
    findFirstTransitionProbabilities(stemmer, emission, transition, separated_line, word_probability_mapping)

    for i in range(len(separated_line) - 1):
        prev_word = splitWordAndTag(stemmer, separated_line[i])[0]
        word = splitWordAndTag(stemmer, separated_line[i + 1])[0]

        for tag in emission:
            emission_probability = calculateEmissionProbability(emission, tag, word)
            temp_mapping = {}

            for prev_probabilities in word_probability_mapping.get(prev_word).items():
                prev_tag, prev_probability = convertDictToTuple(prev_probabilities[1])
                transition_probability = calculateTransitionProbability(transition, tag, prev_tag)
                calculated_probability = prev_probability * transition_probability * emission_probability

                try:
                    temp_mapping[tag][prev_tag] = calculated_probability
                except:
                    temp_mapping[tag] = {prev_tag: calculated_probability}

            max_probability, prev_tag = findMaxProbabilityAndConvertToTuple(temp_mapping)
            addDictionaryToMap(word_probability_mapping, word, tag, prev_tag, max_probability)

    findLastTransitionProbabilities(transition, splitWordAndTag(stemmer, separated_line[-1])[0], word_probability_mapping)
    result_list = tracePath(stemmer, separated_line, word_probability_mapping)
    return compareResults(stemmer, separated_line, result_list[::-1])

start = time.time()
emission, emission_reversed, transition = {}, {}, {}
words_with_tags, lines = [], []
stemmer = Stemmer()

[lines.append('not_a_word/start ' + line.strip() + ' not_a_word/end') for line in open("data.txt", "r").readlines()]
[words_with_tags.append(word.strip()) for line in lines for word in line.split()]


f = open("test.txt", "r")


countEmission(stemmer, emission, emission_reversed, words_with_tags)
countTransition(stemmer, transition, words_with_tags)

correct_false_tuple = (0, 0)
for line in f.readlines():
    words_with_tags_test = line.split()
    temp_tuple = viterbiNew(stemmer, transition, emission, emission_reversed, words_with_tags_test)
    correct_false_tuple = (correct_false_tuple[0] + temp_tuple[0], correct_false_tuple[1] + temp_tuple[1])

print(correct_false_tuple)

true = correct_false_tuple[0]
total = correct_false_tuple[1]

print((true / total) * 100)


end = time.time()
print(end - start)