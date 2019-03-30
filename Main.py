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
    return max([innerDict for innerDict in mapping.items()])


def tracePath(stemmer, separated_line, mapping):
    trace = []
    sizeOfLine = len(separated_line)
    prev_tag = ""
    for i in reversed(range(sizeOfLine)):
        word, tag = splitWordAndTag(stemmer, separated_line[i])

        if i == sizeOfLine - 1:
            found_tag, prev_tag = findMaxProbabilityForLastWord(mapping.get(word))
            trace.append(found_tag)

        else:
            tt = convertDictToTuple(mapping.get(word).get(prev_tag))
            trace.append(prev_tag)
            prev_tag = tt[1]

    return trace


def findFirstTransitionProbabilities(stemmer, emission, transition, separated_line, word_probability_mapping):
    word = splitWordAndTag(stemmer, separated_line[0])[0]
    for tag in emission:
        try:
            transition_probability = (transition.get('start').get(tag) + 1) / (
                        calculateTotalItems(transition.get('start')) + len(transition.get('start')))
        except:
            transition_probability = 0
        try:
            emission_probability = (emission.get(tag).get(word) + 1) / (
                        calculateTotalItems(emission.get(tag)) + len(emission.get(tag)))
        except:
            emission_probability = 1 / (calculateTotalItems(emission.get(tag)) + len(emission.get(tag)))
        try:
            word_probability_mapping[word][tag] = {transition_probability * emission_probability: 'start'}
        except:
            word_probability_mapping[word] = {tag: {transition_probability * emission_probability: 'start'}}


def calculateEmissionProbability(emission, tag ,word):
    emission_probability = 0
    try:
        emission_probability = (emission.get(tag).get(word) + 1) / (
                    calculateTotalItems(emission.get(tag)) + len(emission.get(tag)))
    except:
        emission_probability = 1 / (calculateTotalItems(emission.get(tag)) + len((emission.get(tag))))

    return emission_probability


def calculateTransitionProbability(transition, tag, probability_prev_tag_tuple):
    transition_probability = 0
    try:
        transition_probability = (transition.get(probability_prev_tag_tuple[1]).get(tag) + 1) \
                                 / (calculateTotalItems(transition.get(probability_prev_tag_tuple[1])) + len(
            transition.get(probability_prev_tag_tuple[1])))
    except:
        transition_probability = 0
    return transition_probability


def viterbi(stemmer, transition, emission, separated_line):
    word_probability_mapping = {}
    #todo UNDER CONSTRUCTION STAY AWAKE
    findFirstTransitionProbabilities(stemmer, emission, transition, separated_line, word_probability_mapping)

    for i in range(len(separated_line) - 1):
        prev_word, prev_tag = splitWordAndTag(stemmer, separated_line[i])
        word = splitWordAndTag(stemmer, separated_line[i + 1])[0]

        for tag in emission:
            emission_probability = calculateEmissionProbability(emission, tag, word)
            temp_mapping = {}

            for prev_probabilities in word_probability_mapping.get(prev_word).items():
                probability_prev_tag_tuple = convertDictToTuple(prev_probabilities[1])
                transition_probability = calculateTransitionProbability(transition, tag, probability_prev_tag_tuple)

                try:
                    temp_mapping[tag][probability_prev_tag_tuple[0] * transition_probability * emission_probability] = prev_probabilities[0]
                except:
                    temp_mapping[tag] = {probability_prev_tag_tuple[0] * transition_probability * emission_probability: prev_probabilities[0]}

            max_probability_prev_tag_tuple = findMaxProbabilityAndConvertToTuple(temp_mapping)
            try:
                word_probability_mapping[word][tag] = {max_probability_prev_tag_tuple[0]: max_probability_prev_tag_tuple[1]}
            except:
                word_probability_mapping[word] = {tag: {max_probability_prev_tag_tuple[0]: max_probability_prev_tag_tuple[1]}}

    #todo end transitionu icinde birseyler yapmak lazim
    return tracePath(stemmer, separated_line, word_probability_mapping)


emission, transition = {}, {}
words_with_tags, lines = [], []
stemmer = Stemmer()

[lines.append('not_a_word/start ' + line + 'not_a_word/end ') for line in open("data.txt", "r").readlines()]
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

# mappi = {'a': {'noun': {45: "prev_tag"}}}
# z = max([n for m in mapps.values() for n in m.items()])

# print(z)
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

cc = viterbi(stemmer,transition,emission,deneme5)
print(cc[::-1])
