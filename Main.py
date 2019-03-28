
def wordOrganizer(word):
    word = word.replace("_"," ")
    if '\'' in word:
        n = word[0:int(word.find('\''))]
        return n.lower()
    return word.lower()


def splitWordAndTag(word_with_tag):
    separation = word_with_tag.split('/')
    word = wordOrganizer(separation[0])
    tag = wordOrganizer(separation[1])
    return word, tag


def countEmission(emission, words_with_tags):
    for word_with_tag in words_with_tags:
        word = splitWordAndTag(word_with_tag)[0]
        tag = splitWordAndTag(word_with_tag)[1]

        try:
            emission[tag][word] += 1
        except KeyError:
            try:
                emission[tag][word] = 1
            except KeyError:
                emission[tag] = {word: 1}


def countTransition(transition, word_with_tags):
    for i in range(len(words_with_tags) - 1):
        tag = splitWordAndTag(words_with_tags[i])[1]
        next_tag = splitWordAndTag(words_with_tags[i + 1])[1]

        try:
            transition[tag][next_tag] += 1
        except KeyError:
            try:
                transition[tag][next_tag] = 1
            except KeyError:
                transition[tag] = {next_tag: 1}


f = open("metu.txt", "r")
emission = {}
transition = {}

words_with_tags = []
[words_with_tags.append(word.strip()) for line in f.readlines() for word in line.split()]

countEmission(emission, words_with_tags)
countTransition(transition, words_with_tags)

print(emission.get('verb'))
print(transition.get('verb'))