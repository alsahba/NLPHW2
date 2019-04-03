import math, time
from Stemmer import Stemmer


def calculateTotalItems(mapping):
    return sum(count for word, count in mapping.items())


def splitWordAndTag(stemmer, word_with_tag):
    separation = word_with_tag.split('/')
    word = stemmer.wordOrganizer(separation[0])
    tag = stemmer.wordOrganizer(separation[1])
    return word, tag


def countEmission(stemmer, emission, words_with_tags):
    for word_with_tag in words_with_tags:
        word, tag = splitWordAndTag(stemmer, word_with_tag)

        if word == 'not a word':
            continue
        addDictionaryToMap(emission, tag, word)


def countTransition(stemmer, transition, word_with_tags):
    for i in range(len(words_with_tags) - 1):
        tag = splitWordAndTag(stemmer, words_with_tags[i])[1]
        next_tag = splitWordAndTag(stemmer, words_with_tags[i + 1])[1]

        if tag == 'end' and next_tag == 'start':
            continue
        addDictionaryToMap(transition, tag, next_tag)


def findMaxProbabilityAndConvertToTuple(mapping):
    return max([inner_dict for outer_dict in mapping.values() for inner_dict in outer_dict.items()])

#
# def findMaxProbabilityForLastWord(mapping):
#     max_probability, temp_tuple = 0, ()
#     [map(max_probability, inner_dict[0]) and map(temp_tuple, (outer_dict[0], inner_dict[1])) for outer_dict in mapping.items() for inner_dict in outer_dict[1].items()]
#     return temp_tuple
#

def convertDictToTuple(mapping):
    return [innerDict for innerDict in mapping.items()][0]


def tracePath(stemmer, separated_line, mapping):
    trace = []
    sizeOfLine = len(separated_line)
    prev_tag = convertDictToTuple(mapping.get('not a word').get('end'))[1]

    for i in reversed(range(sizeOfLine)):
        word = splitWordAndTag(stemmer, separated_line[i])[0]
        trace.append(prev_tag)
        prev_tag = convertDictToTuple(mapping.get(word).get(prev_tag))[1]
    return trace


def calculateTransitionProbability(transition, tag, prev_tag):
    denominator = calculateTotalItems(transition.get(prev_tag))
    try:
        transition_probability = float((transition.get(prev_tag).get(tag)) / denominator)
    except:
        transition_probability = 0.00000001
    return math.log2(transition_probability)


def calculateEmissionProbability(emission, tag, word):
    denominator = calculateTotalItems(emission.get(tag))
    try:
        emission_probability = float((emission.get(tag).get(word)) / denominator)
    except:
        emission_probability = 0.00000001
    return math.log2(emission_probability)


def findFirstTransitionProbabilities(stemmer, emission, transition, separated_line, word_probability_mapping):
    word = splitWordAndTag(stemmer, separated_line[0])[0]
    for tag in emission:
        transition_probability = calculateTransitionProbability(transition, tag, 'start')
        emission_probability = calculateEmissionProbability(emission, tag, word)
        addDictionaryToMap(word_probability_mapping, word, tag, transition_probability + emission_probability, 'start')


def findLastTransitionProbabilities(transition, prev_word, word_probability_mapping):
    max_probability = -500000000000
    for tag in transition:
        if tag == 'start':
            continue

        transition_probability = calculateTransitionProbability(transition, 'end', tag)
        probability_prev_tag_tuple = convertDictToTuple(word_probability_mapping.get(prev_word).get(tag))
        calculated_probability = probability_prev_tag_tuple[0] + transition_probability

        if max_probability <= calculated_probability:
            max_probability = calculated_probability
            addDictionaryToMap(word_probability_mapping, 'not a word', 'end', calculated_probability, tag)


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
                prev_probability, prev_tag = convertDictToTuple(prev_probabilities[1])
                transition_probability = calculateTransitionProbability(transition, tag, prev_tag)
                calculated_probability = prev_probability + transition_probability + emission_probability

                try:
                    temp_mapping[tag][calculated_probability] = prev_probabilities[0]
                except:
                    temp_mapping[tag] = {calculated_probability: prev_probabilities[0]}


            max_probability, prev_tag = findMaxProbabilityAndConvertToTuple(temp_mapping)
            addDictionaryToMap(word_probability_mapping, word, tag, max_probability, prev_tag)

    findLastTransitionProbabilities(transition, splitWordAndTag(stemmer, separated_line[-1])[0], word_probability_mapping)
    result_list = tracePath(stemmer, separated_line, word_probability_mapping)
    return compareResults(stemmer, separated_line, result_list[::-1])

start = time.time()
emission, transition = {}, {}
words_with_tags, lines = [], []
stemmer = Stemmer()

[lines.append('not_a_word/start ' + line.strip() + ' not_a_word/end') for line in open("data.txt", "r").readlines()]
[words_with_tags.append(word.strip()) for line in lines for word in line.split()]


f = open("test.txt", "r")


countEmission(stemmer, emission, words_with_tags)
countTransition(stemmer, transition, words_with_tags)

correct_false_tuple = (0, 0)
for line in f.readlines():
    words_with_tags_test = line.split()
    temp_tuple = viterbi(stemmer, transition, emission, words_with_tags_test)
    correct_false_tuple = (correct_false_tuple[0] + temp_tuple[0], correct_false_tuple[1] + temp_tuple[1])

print(correct_false_tuple)

true = correct_false_tuple[0]
total = correct_false_tuple[1]

print((true / total) * 100)
end = time.time()
print(end - start)