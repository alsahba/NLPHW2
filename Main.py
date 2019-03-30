from Stemmer import Stemmer
import math

def calculateTotalNumberOfTwoLayerMapping(mapping):
    return sum(count for outerScope in mapping.items() for word, count in outerScope[1].items())


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
    return max([innerDict for outerDict in mapping.values() for innerDict in outerDict.items()])


def converDictToTuple(mapping):
    return max([innerDict for innerDict in mapping.items()])


def calculateProbability(stemmer, transition, emission, separated_line):
    mapo = {}
    #todo UNDER CONSTRUCTION STAY AWAKE
    word, tag = splitWordAndTag(stemmer, separated_line[0])
    for m in emission:
        try:
            calcTransition = transition.get('start').get(m) / calculateTotalItems(transition.get('start'))
        except:
            calcTransition = 0.0000000001
        try:
            calcEmission = emission.get(m).get(word) / calculateTotalItems(emission.get(m))
        except:
            #todo laplace gerekiyor burada
            calcEmission = 0.00000000001
        try:
            mapo[word][m] = {calcTransition * calcEmission: 'start'}
        except:
            mapo[word] = {m: {calcTransition * calcEmission: 'start'}}

    for i in range(len(separated_line) - 1):
        prev_word, prev_tag = splitWordAndTag(stemmer, separated_line[i])
        word, tag = splitWordAndTag(stemmer, separated_line[i + 1])

        for m in emission:
            try:
                calcEmission = emission.get(m).get(word) / calculateTotalItems(emission.get(m))
            except:
                # todo laplace gerekiyor burada
                calcEmission = 0.00000000001
            tempmapo = {}
            for n in mapo[prev_word].items():
                t = converDictToTuple(n[1])
                try:
                    calcTransition = transition.get(t[1]).get(m) / calculateTotalItems(transition.get(t[1]))
                    try:
                        tempmapo[m][t[0] * calcTransition * calcEmission] = n[0]
                    except:
                        tempmapo[m]= {t[0] * calcTransition * calcEmission: n[0]}
                except:
                    try:
                        tempmapo[m][t[0] * 0.00000000001 * calcEmission] = n[0]
                    except:
                        tempmapo[m] = {t[0] * 0.00000000001 * calcEmission : n[0]}

            ali = findMaxProbabilityAndConvertToTuple(tempmapo)
            try:
                mapo[word][m] = {ali[0]: ali[1]}
            except:
                mapo[word] = {m: {ali[0]: ali[1]}}

    #todo KARSILASTIRMA FONKSIYONU YAZILACAK BURAYA SEP_LINE I VE MAPOYU ALABILIRIZ
    for w in separated_line:
        wor,tag = splitWordAndTag(stemmer,w)
        print("{} - {}".format(wor, findMaxProbabilityAndConvertToTuple(mapo.get(wor))))


emission, transition = {}, {}
words_with_tags, lines = [], []
stemmer = Stemmer()

[lines.append('not_a_word/start ' + line + 'not_a_word/end ') for line in open("data.txt", "r").readlines()]
[words_with_tags.append(word.strip()) for line in lines for word in line.split()]

countEmission(stemmer, emission, words_with_tags)
countTransition(stemmer, transition, words_with_tags)

deneme = ["Siz/Pron", ",/Punc", "sonsuza/Noun", "dek/Postp", "yürüyeceksiniz/Verb", "./Punc"]


mapps = {'noun': {45: "prev_tag"}, 'un': {60: "prev_tag"},'oun': {80: "prev_tag"}}
maxdict = {'non':{0: 'non'}}

z = max([n for m in mapps.values() for n in m.items()])

# print(z)
    # print(max(m))
    # for n in m:
    #     if ()
    #     # maxdict = m[1][0]
# print(maxdict)
# k = converDictToTuple(mapps)
# print(k)


# print(calculateTotalNumberOfTwoLayerMapping(emission))
# print(calculateTotalNumberOfTwoLayerMapping(transition))
# print(emission.get('start'))
# print(transition.get('punc'))

cc = calculateProbability(stemmer,transition,emission,deneme)
# print(cc)
