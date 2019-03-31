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


def findMaxProbabilityForLastWord(mapping):
    max_probability = 0
    temp_tuple = ()

    for outer_dict in mapping.items():
        for inner_dict in outer_dict[1].items():
            if max_probability < inner_dict[0]:
                max_probability = inner_dict[0]
                temp_tuple = (outer_dict[0], inner_dict[1])
    return temp_tuple


def convertDictToTuple(mapping):
    return [innerDict for innerDict in mapping.items()][0]


def tracePath(stemmer, separated_line, mapping):
    trace = []
    sizeOfLine = len(separated_line)
    prev_tag = convertDictToTuple(mapping.get('not a word').get('end'))[1]
    for i in reversed(range(sizeOfLine)):
        word, tag = splitWordAndTag(stemmer, separated_line[i])
        trace.append(prev_tag)
        prev_tag = convertDictToTuple(mapping.get(word).get(prev_tag))[1]
    return trace


def calculateTransitionProbability(transition, tag, prev_tag):
    try:
        transition_probability = (transition.get(prev_tag).get(tag) + 1) \
                                 / (calculateTotalItems(transition.get(prev_tag)) + len(
            transition.get(prev_tag)))
    except:
        transition_probability = 0
    return transition_probability


def calculateEmissionProbability(emission, tag, word):
    try:
        emission_probability = (emission.get(tag).get(word) + 1) / (
                    calculateTotalItems(emission.get(tag)) + len(emission.get(tag)))
    except:
        emission_probability = 1 / (calculateTotalItems(emission.get(tag)) + len((emission.get(tag))))

    return emission_probability


def findFirstTransitionProbabilities(stemmer, emission, transition, separated_line, word_probability_mapping):
    word = splitWordAndTag(stemmer, separated_line[0])[0]
    for tag in emission:
        transition_probability = calculateTransitionProbability(transition, tag, 'start')
        emission_probability = calculateEmissionProbability(emission, tag, word)
        addDictionaryToMap(word_probability_mapping, word, tag, transition_probability * emission_probability, 'start')


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


def findLastTransitionProbabilities(transition, prev_word, word_probability_mapping):
    max_probability = 0
    for tag in transition:
        if tag == 'start':
            continue

        transition_probability = calculateTransitionProbability(transition, 'end', tag)
        probability_prev_tag_tuple = convertDictToTuple(word_probability_mapping.get(prev_word).get(tag))
        calculated_probability = probability_prev_tag_tuple[0] * transition_probability

        if max_probability < calculated_probability:
            max_probability = calculated_probability
            addDictionaryToMap(word_probability_mapping, 'not a word', 'end', calculated_probability, tag)


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
                probability_prev_tag_tuple = convertDictToTuple(prev_probabilities[1])
                transition_probability = calculateTransitionProbability(transition, tag, probability_prev_tag_tuple[1])
                calculated_probability = probability_prev_tag_tuple[0] * transition_probability * emission_probability

                try:
                    temp_mapping[tag][calculated_probability] = prev_probabilities[0]
                except:
                    temp_mapping[tag] = {calculated_probability: prev_probabilities[0]}

            max_probability_prev_tag_tuple = findMaxProbabilityAndConvertToTuple(temp_mapping)
            temp_mapping.clear()
            addDictionaryToMap(word_probability_mapping, word, tag, max_probability_prev_tag_tuple[0], max_probability_prev_tag_tuple[1])

    findLastTransitionProbabilities(transition, splitWordAndTag(stemmer, separated_line[-1])[0], word_probability_mapping)
    return tracePath(stemmer, separated_line, word_probability_mapping)


emission, transition = {}, {}
words_with_tags, lines = [], []
stemmer = Stemmer()

[lines.append('not_a_word/start ' + line.strip() + ' not_a_word/end') for line in open("data.txt", "r").readlines()]
[words_with_tags.append(word.strip()) for line in lines for word in line.split()]

countEmission(stemmer, emission, words_with_tags)
countTransition(stemmer, transition, words_with_tags)

deneme = ["Siz/Pron", ",/Punc", "sonsuza/Noun", "dek/Postp", "yürüyeceksiniz/Verb", "./Punc"]
deneme2 = ["Erkekler_Parkı'na/Noun", "gidiyorsun/Verb", "./Punc"]
deneme3 = ["Sürpriz/Noun", "ne/Pron", "acaba/Adv", "?/Punc"]
deneme4 = ["Sağındaki/Adj", "taburede/Noun", "de/Conj", "darbukasıyla/Noun", ",/Punc", "Recep/Noun", "olurdu/Verb", "./Punc"]
deneme5 = ["Dışarıya/Noun", "bakın/Verb", "./Punc"]
# mapps = {'noun': {45: "prev_tag"}, 'un': {60: "prev_tag"},'oun': {80: "prev_tag"}}
# maxdict = {'non':{0: 'non'}}

mappi = {'a': {'noun': {45: "prev_tag"}}}
# z = max([n for m in mapps.values() for n in m.items()])


print(convertDictToTuple(mappi.get('a').get('noun')))
    # print(max(m))
    # for n in m:
    #     if ()
    #     # maxdict = m[1][0]
# print(maxdict)
# k = convertDictToTuple(mapps)
# print(convertDictToTuple(mappi.get('a')))
# print(findMaxProbabilityForLastWord(mappi.get('a')))

# print(calculateTotalNumberOfTwoLayerMapping(emission))
# print(calculateTotalNumberOfTwoLayerMapping(transition))
# print(emission.get('start'))
# print(transition.get('punc'))

cc = viterbi(stemmer, transition, emission, deneme)
print(cc[::-1])
