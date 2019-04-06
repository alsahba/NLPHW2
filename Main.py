import time, numpy as np
# from snowballstemmer import stemmer


# turkishStemmer = stemmer("turkish")


def calculateTotalItems(mapping):
    return sum(count for word, count in mapping.items())


def wordOrganizer(word):

    word = word.replace("_", " ")
    if '\'' in word:
        word = word[0:int(word.find('\''))]
        # word = turkishStemmer.stemWord(word)
        return word.lower()
    # if word != 'not a word':
        # word = turkishStemmer.stemWord(word)
    return word.lower()


def splitWordAndTag(word_with_tag):
    separation = word_with_tag.split('/')
    word = wordOrganizer(separation[0])
    tag = separation[1].lower()
    return word, tag


def observeEmission(emission, emission_reversed, words_with_tags):
    for word_with_tag in words_with_tags:
        word, tag = splitWordAndTag(word_with_tag)

        if word == 'not a word':
            continue

        addDictionaryToMapDuple(emission, tag, word)
        addDictionaryToMapDuple(emission_reversed, word, tag)


def observeTransition(transition, words_with_tags):
    for index in range(len(words_with_tags) - 1):
        tag = splitWordAndTag(words_with_tags[index])[1]
        next_tag = splitWordAndTag(words_with_tags[index + 1])[1]

        if tag == 'end' and next_tag == 'start':
            continue

        addDictionaryToMapDuple(transition, tag, next_tag)


def findMaxProbabilityAndConvertToTuple(mapping):
    return max([(inner_dict[1], inner_dict[0]) for outer_dict in mapping.items() for inner_dict in outer_dict[1].items()])


def tracePath(separated_line, array):
    trace, sizeOfLine = [], len(separated_line)
    prev_tag = array[sizeOfLine].get('end')[0]

    for index in reversed(range(sizeOfLine)):
        trace.append(prev_tag)
        prev_tag = array[index].get(prev_tag)[0]
    return trace


def calcTransitionProbability(transition, tag, prev_tag):
    denominator = calculateTotalItems(transition.get(prev_tag)) + len(transition.get(prev_tag))
    try:
        transition_probability = (transition.get(prev_tag).get(tag)) / denominator
    except (KeyError, TypeError):
        transition_probability = 1 / denominator
    return transition_probability


def calcEmissionProbability(emission, tag, word):
    denominator = calculateTotalItems(emission.get(tag))
    # denominator = calculateTotalItems(emission.get(tag)) + len(emission.get(tag))
    try:
        emission_probability = (emission.get(tag).get(word)) / denominator
    except (KeyError, TypeError):
        emission_probability = 0
        # emission_probability = 1 / denominator
    return emission_probability


def addDictionaryToArray(array, index, tag, prev_tag, probability):
    try:
        array[index][tag] = (prev_tag, probability)
    except (KeyError, TypeError):
        array[index] = {tag: (prev_tag, probability)}


def calcInitialProbability(emission, emission_reversed, transition, separated_line, word_probability_array):
    word = splitWordAndTag(separated_line[0])[0]
    for tag in emission:
        transition_probability = calcTransitionProbability(transition, tag, 'start')
        emission_probability = calcEmissionProbability(emission, tag, word)
        calculated_probability = transition_probability * emission_probability

        if emission_reversed.get(word) is None:
            calculated_probability = transition_probability

        addDictionaryToArray(word_probability_array, 0, tag, 'start', calculated_probability)


def calcLastProbability(transition, word_probability_array, index):
    max_probability = 0
    for tag in transition:
        if tag == 'start':
            continue

        transition_probability = calcTransitionProbability(transition, 'end', tag)
        probability_tuple = word_probability_array[index].get(tag)
        calculated_probability = probability_tuple[1] * transition_probability

        if max_probability <= calculated_probability:
            max_probability = calculated_probability
            addDictionaryToArray(word_probability_array, index + 1, 'end', tag, calculated_probability)


def addDictionaryToMapDuple(mapping, tag, tag_word):
    try:
        mapping[tag][tag_word] += 1
    except (KeyError, TypeError):
        try:
            mapping[tag][tag_word] = 1
        except (KeyError, TypeError):
            mapping[tag] = {tag_word: 1}


def addDictionaryToMapTriple(mapping, tag, prev_tag, probability):
    try:
        mapping[tag][prev_tag] = probability
    except (KeyError, TypeError):
        mapping[tag] = {prev_tag: probability}


def compareResults(separated_line, result_list):
    correct_result = sum([1 for index, word_with_tag in enumerate(separated_line)
                          if splitWordAndTag(word_with_tag)[1] == result_list[index]])
    return correct_result, len(separated_line)


def viterbi(transition, emission, emission_reversed, separated_line):
    word_probability_array = np.empty(len(separated_line) + 1, dtype=dict)
    calcInitialProbability(emission, emission_reversed, transition, separated_line, word_probability_array)
    index = 0
    for index in range(len(separated_line) - 1):
        word = splitWordAndTag(separated_line[index + 1])[0]

        for tag in emission:
            emission_probability = calcEmissionProbability(emission, tag, word)
            temp_mapping = {}

            for prev_tag, prev_probability in word_probability_array[index].items():
                transition_probability = calcTransitionProbability(transition, tag, prev_tag)
                calculated_probability = prev_probability[1] * transition_probability * emission_probability

                if emission_probability == 0 and emission_reversed.get(word) is None:
                    calculated_probability = prev_probability[1] * transition_probability
                addDictionaryToMapTriple(temp_mapping, tag, prev_tag, calculated_probability)

            max_probability, found_prev_tag = findMaxProbabilityAndConvertToTuple(temp_mapping)
            addDictionaryToArray(word_probability_array, index + 1, tag, found_prev_tag, max_probability)

    calcLastProbability(transition, word_probability_array, index + 1)
    return word_probability_array


def testData(test_lines, transition, emission, emission_reversed):
    correct_false_tuple = (0, 0)
    for line in test_lines:
        words_with_tags_test = line.split()
        word_probability_array = viterbi(transition, emission, emission_reversed, words_with_tags_test)
        found_path = tracePath(words_with_tags_test, word_probability_array)
        temp_tuple = compareResults(words_with_tags_test, found_path[::-1])
        correct_false_tuple = (correct_false_tuple[0] + temp_tuple[0], correct_false_tuple[1] + temp_tuple[1])
    return correct_false_tuple


def main():
    start = time.time()
    emission, emission_reversed, transition = {}, {}, {}
    words_with_tags, train_lines, test_lines = [], [], []

    [train_lines.append('not_a_word/start ' + line.strip() + ' not_a_word/end') if index < 3960
     else test_lines.append(line.strip()) for index, line in enumerate(open("metu.txt", "r").readlines())]
    [words_with_tags.append(word.strip()) for line in train_lines for word in line.split()]

    observeEmission(emission, emission_reversed, words_with_tags)
    observeTransition(transition, words_with_tags)

    correct_false_tuple = testData(test_lines, transition, emission, emission_reversed)
    print("Accuracy is {0:0.2f} percent for 1699 lines.".format((correct_false_tuple[0] / correct_false_tuple[1]) * 100))
    print("Running time took {0:0.2f} seconds".format(time.time() - start))


main()
