import numpy as np
# from snowballstemmer import stemmer
# turkishStemmer = stemmer("turkish")

# NOTE: Commented lines show different ways of calculating probability or counting.
# They are commented because of highest accuracy found in this way, other ways are not as good as this solution.

# This method used for calculating total number of items in the emission or transition mapping.
def calculateTotalItems(mapping):
    return sum(count for word, count in mapping.items())


# This method used for word's letter and punctuation handling. It cuts the word after cutting mark and converts
# word's all letters to lowercase.
def wordOrganizer(word):
    word = word.replace("_", " ")
    if '\'' in word:
        word = word[0:int(word.find('\''))]
        # word = turkishStemmer.stemWord(word)
        return word.lower()
    # if word != 'not a word':
        # word = turkishStemmer.stemWord(word)
    return word.lower()


# This method used for separation of word and its tag, returns a tuple.
def splitWordAndTag(word_with_tag):
    separation = word_with_tag.split('/')
    word = wordOrganizer(separation[0])
    tag = separation[1].lower()
    return word, tag


# This method used for counting the repeated number of emissions. Bigram mapping used for storing tag-word tuples.
# Handle of the start and end tags made with if condition, special word (not a word) did not count as an emission.
# Two dictionary used for emission mapping, one of them holds tuples like tag: {word1, word2 ...},
# other of them holds tuples like word1: {tag1, tag2 ...}
# This two way of storing helps calculation of probability for viterbi algorithm.
def observeEmission(emission, emission_reversed, words_with_tags):
    for word_with_tag in words_with_tags:
        word, tag = splitWordAndTag(word_with_tag)

        if word == 'not a word':
            continue

        addDictionaryToMapDuple(emission, tag, word)
        addDictionaryToMapDuple(emission_reversed, word, tag)


# This method used for counting the repeated number of transitions. Bigram mapping used for storing tag-prev_tag tuples.
# Handle of the end and start tags made with if condition, end-start tags did not count as an transition.
# One dictionary structure used for transition mapping, it is like tag: {next_tag1, next_tag2 ...}
def observeTransition(transition, words_with_tags):
    for index in range(len(words_with_tags) - 1):
        tag = splitWordAndTag(words_with_tags[index])[1]
        next_tag = splitWordAndTag(words_with_tags[index + 1])[1]

        if tag == 'end' and next_tag == 'start':
            continue

        addDictionaryToMapDuple(transition, tag, next_tag)


# This method used for calculating max probability for viterbi algorithm.
# Previous words all tags are tried and put in temporary dictionary structure.
# With this algorithm max probability found and then algorithm can decide which tag is used for previous word.
# Returns a tuple that includes max probability and tag.
def findMaxProbabilityAndConvertToTuple(mapping):
    return max([(inner_dict[1], inner_dict[0]) for outer_dict in mapping.items() for inner_dict in outer_dict[1].items()])


# This method used for tracing end to start for accuracy calculation.
# Decide which tag is followed by end, then iteratively found previous tag that followed by current tag through start.
# All previous tags added to a list and return that list.
def tracePath(separated_line, array):
    trace, size_of_line = [], len(separated_line)
    prev_tag = array[size_of_line].get('end')[0]

    for index in reversed(range(size_of_line)):
        trace.append(prev_tag)
        prev_tag = array[index].get(prev_tag)[0]
    return trace


# This method used for calculating transition probability for previous tag to current tag by looking transition bigram mapping.
# Add one smoothing used for unseen transitions.
def calcTransitionProbability(transition, tag, prev_tag):
    denominator = calculateTotalItems(transition.get(prev_tag)) + len(transition.get(prev_tag))
    try:
        transition_probability = (transition.get(prev_tag).get(tag)) / denominator
    except (KeyError, TypeError):
        transition_probability = 1 / denominator
    return transition_probability


# This method used for calculating emission probability for known tag and word but looking emission bigram mapping.
# Add one smoothing did not use for unseen emissions, purpose of this is higher accuracy maintained by this solution.
# Another solution with add one smoothing commented in this method.
def calcEmissionProbability(emission, tag, word):
    denominator = calculateTotalItems(emission.get(tag))
    # denominator = calculateTotalItems(emission.get(tag)) + len(emission.get(tag))
    try:
        emission_probability = (emission.get(tag).get(word)) / denominator
    except (KeyError, TypeError):
        emission_probability = 0
        # emission_probability = 1 / denominator
    return emission_probability


# This method used for adding elements to probability array.
def addDictionaryToArray(array, index, tag, prev_tag, probability):
    try:
        array[index][tag] = (prev_tag, probability)
    except (KeyError, TypeError):
        array[index] = {tag: (prev_tag, probability)}


# This method used for calculation of first transition from start to first word.
# There is a handle mechanism used for unseen emission, reason of that is higher accuracy provided by this solution.
# If word has not been seen before, we look only transition probability,
# skipped emission probability which is equal to zero.
# All tag transition probabilities calculated with emission probability and put into the array.
def calcInitialProbability(emission, emission_reversed, transition, separated_line, word_probability_array):
    word = splitWordAndTag(separated_line[0])[0]
    for tag in emission:
        transition_probability = calcTransitionProbability(transition, tag, 'start')
        emission_probability = calcEmissionProbability(emission, tag, word)
        calculated_probability = transition_probability * emission_probability

        if emission_reversed.get(word) is None:
            calculated_probability = transition_probability

        addDictionaryToArray(word_probability_array, 0, tag, 'start', calculated_probability)


# This method used for calculation of last transition probability.
# Maximum probability of last word's tags to 'end' tag probability is calculated and found, then added to array.
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


# This method used for counting and adding elements for emission or transition mappings.
def addDictionaryToMapDuple(mapping, tag, tag_word):
    try:
        mapping[tag][tag_word] += 1
    except (KeyError, TypeError):
        try:
            mapping[tag][tag_word] = 1
        except (KeyError, TypeError):
            mapping[tag] = {tag_word: 1}


# This method used for adding elements to a mapping for viterbi algorithm.
def addDictionaryToMapTriple(mapping, tag, prev_tag, probability):
    try:
        mapping[tag][prev_tag] = probability
    except (KeyError, TypeError):
        mapping[tag] = {prev_tag: probability}


# This method used for comparing viterbi algorithm's result and actual data in one line.
def compareResults(separated_line, result_list):
    correct_result = sum([1 for index, word_with_tag in enumerate(separated_line)
                          if splitWordAndTag(word_with_tag)[1] == result_list[index]])
    return correct_result, len(separated_line)


# Viterbi algorithm implementation.
# Firstly an array is created. In this solution array-dictionary hybrid structure used.
# Array part is for words in one line. All words associated with indexes. Last index reserved for 'end' tag.
# Initial probability calculated and added to map, then iteratively all words flowed for this algorithm.
# Calculation mechanism is in general previous_probability * transition_probability * emission_probability. But,
# if word has not been seen before calculation made with previous_probability * transition_probability
# like calculation of initial probability. The reason for that is higher accuracy.
# Previous word's all tags are tried for one tag transition and added to temporary map,
# then maximum probability is found and added to map.
# In the end array is returned.
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


# This method used for testing the viterbi algorithm implementation with using test data.
# In the end a tuple that includes correct detection and total number returned.
def testData(test_lines, transition, emission, emission_reversed):
    correct_false_tuple = (0, 0)
    for line in test_lines:
        words_with_tags_test = line.split()
        word_probability_array = viterbi(transition, emission, emission_reversed, words_with_tags_test)
        found_path = tracePath(words_with_tags_test, word_probability_array)
        temp_tuple = compareResults(words_with_tags_test, found_path[::-1])
        correct_false_tuple = (correct_false_tuple[0] + temp_tuple[0], correct_false_tuple[1] + temp_tuple[1])
    return correct_false_tuple


# Main method.
def main():
    emission, emission_reversed, transition = {}, {}, {}
    words_with_tags, train_lines, test_lines = [], [], []

    [train_lines.append('not_a_word/start ' + line.strip() + ' not_a_word/end') if index < 3960
     else test_lines.append(line.strip()) for index, line in enumerate(open("metu.txt", "r").readlines())]
    [words_with_tags.append(word.strip()) for line in train_lines for word in line.split()]

    observeEmission(emission, emission_reversed, words_with_tags)
    observeTransition(transition, words_with_tags)

    correct_false_tuple = testData(test_lines, transition, emission, emission_reversed)
    print("Accuracy is {0:0.2f} percent for 1699 lines.".format((correct_false_tuple[0] / correct_false_tuple[1]) * 100))


main()
