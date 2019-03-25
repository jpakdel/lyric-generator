"""
This file is used to do textual analysis of the entire rap corpus, as well as 
rate the sentences we create via markov chains in relation to said textual analysis.
"""



from gensim.models import Word2Vec
import rhyme_distances as rdist
from word_processor import find_viable_words
from word_embedder import get_unique_words, create_entry, is_unique
from helper_methods import get_all_sentence_array, jprint
import json


viable_words = find_viable_words()

test_sents = {
    "data":[

    ]
}
tuning_params = {"meaning": [0.3, 0.5, 0.7], "rhyme": [0.5,0.6,0.7], "start-sound": [0.5,0.6,0.7]}



def load_analysis_files(intra):
    pos = "extra"
    if intra:
        pos = "intra"
    analysis_types = {"meaning": {}, "rhyme": {}, "start-sound": {}}
    for type in analysis_types:
        file_name = pos + "_" + type + "_corp.json"
        with open(file_name) as f:
            data = json.load(f)
            analysis_types[type] = data
    return analysis_types

analysis_data = load_analysis_files(True)
model = Word2Vec.load('model.bin')


def find_rhymes():
    global viable_words
    total_rhymes = {}
    for word in viable_words:
        total_rhymes[word] = {}
    sentences = get_all_sentence_array()
    for i, sent in enumerate(sentences):
        print(i)
        try:
            next_sent = sentences[i+1]
            if len(sent) > 2 and len(next_sent) > 2:
                last_word = sent[len(sent)-1]
                last_word_2 = next_sent[len(next_sent)-1]
                if last_word_2 in viable_words and last_word in viable_words:
                    rhyme_similarity = calculate_similarity(last_word, last_word_2, "r")
                    if rhyme_similarity >= 0.66:
                        if last_word_2 not in total_rhymes[last_word]:
                            total_rhymes[last_word][last_word_2] = {
                                "similarity": rhyme_similarity,
                                "count": 0
                            }
                        if last_word not in total_rhymes[last_word_2]:
                            total_rhymes[last_word_2][last_word] = {
                                "similarity": rhyme_similarity,
                                "count": 0
                            }
                        total_rhymes[last_word][last_word_2]["count"] +=1
                        total_rhymes[last_word_2][last_word]["count"] += 1

        except IndexError:
            pass
    with open("rhymes\\master_rhymes.json", 'w') as outfile:
        json.dump(total_rhymes, outfile, indent=4)


def calculate_similarity(word, next_word, category):
    global model
    if word == next_word:
        #print("same")
        return 0
    if category is "rhyme" or category is "r":
        similarity = 1 - rdist.dist(word, next_word, False)
    elif category is "start-sound" or category is "ss" or category[0] =='s':
        similarity = 1 - rdist.dist(word, next_word, True)
    elif category is "meaning" or category is "m":
        similarity = model.wv.similarity(word, next_word)
    elif category is "assonance" or category is "a":
        similarity = model.wv.similarity(word, next_word)

    return similarity

#find_rhymes()


def retrieve_word_dict(word, length):
    global  analysis_data
    entry1 = {"comp_ratio": [], "sent_ratio": []}
    entry2 = {"comp_ratio": [], "sent_ratio": []}
    entry3 = {"comp_ratio": [], "sent_ratio": []}
    output = {"meaning": entry2, "rhyme": entry1,  "start-sound": entry3}
    length = str(length)
    for item in analysis_data:
        try:
            data = analysis_data[item]['word_list'][word]
            sent_count = data['sent_count'][length]
            comp_count = data['comp_count'][length]
            for metric in data:
                if "match" in metric:
                    met = data[metric][length]
                    output[item]["comp_ratio"].append( (round(float(met/comp_count),3)) )
                    output[item]["sent_ratio"].append((round(float(met/sent_count),3)))
        except KeyError:
            pass
    return output

def retrieve_word_array(word, length):
    global  analysis_data
    output = []
    length = str(length)
    for item in analysis_data:
        try:
            data = analysis_data[item]['word_list'][word]
            sent_count = data['sent_count'][length]
            comp_count = data['comp_count'][length]
            for metric in data:
                if "match" in metric:
                    met = data[metric][length]
                    output.append( (round(float(met/comp_count),3)) )
                    output.append((round(float(met/sent_count),3)))
        except KeyError:
            pass
    return output

#print(retrieve_word_array("bitch", 3))

def forecast_sentence(sent, option):
    #predicts expected values for a sentence
    output = {"expected": {}}
    l = len(sent)
    for i, word in enumerate(sent):
        if option:
            output["expected"][str(i+1) + " - " + word ] = retrieve_word_dict(word, l)
        else:
            output["expected"][str(i+1) + " - " + word ] = retrieve_word_array(word, l)
    return output

sample = ['she', 'was', 'done', 'fucked', 'up']

sample2 = ['i', 'know', 'that', 'was', 'pitiful']
#print(json.dumps(forecast_sentence(sample, True), indent=4))



def rank_one_word_in_sent(i, sent):
    #used two rank two words in every single metric in relation to the tuning params
    global tuning_params, model
    word = sent[i]
    key = str(i+1) + " - " + word
    output = {key:[]}
    l = len(sent)

    for param in tuning_params:
        #print()
        #print(word)
        #print(param)
        for val in tuning_params[param]:
            sum = 0
            for j, next_word in enumerate(sent):
                if i != j:
                    similarity = calculate_similarity(word, sent[j], param)
                    if param == "meaning" and (is_unique(word) is False or is_unique(next_word) is False):
                        similarity = 0
                    #print()
                    #print(next_word)
                    #print(similarity)

                    if similarity >= val:
                        #print(word + " " + next_word)
                        sum +=1
            output[key].append(sum)
    #print(output)
    return output


def rank_one_word_to_other_sent(i, sent, word):
    #used two rank two words in every single metric in relation to the tuning params
    global tuning_params, model
    key = str(i+1) + " - " + word
    output = {key:[]}
    l = len(sent)

    for param in tuning_params:
        #print()
        #print(word)
        #print(param)
        for val in tuning_params[param]:
            sum = 0
            for j, next_word in enumerate(sent):
                    similarity = calculate_similarity(word, next_word, param)
                    if param == "meaning" and (is_unique(word) is False or is_unique(next_word) is False):
                        similarity = 0
                    #print()
                    #print(next_word)
                    #print(similarity)

                    if similarity >= val:
                        #print(word + " " + next_word)
                        sum +=1
            output[key].append(sum)
    return output

#print(json.dumps((rank_one_word_in_sent(0,sample)), indent=4))

def rank_one_sentence(sent):
    output = {"actual": {}}

    for i, word in enumerate(sent):
        data = rank_one_word_in_sent(i, sent)
        for d in data:
            output["actual"][d] = data[d]

    return output

def rank_two_sentences(sent_1, sent_2):
    output = {"actual": {}}
    for i, word in enumerate(sent_1):
        sent = sent_2.append(word)
        data = rank_one_word_in_sent(len(sent)-1, sent)
        for d in data:
            output["actual"][d] = data[d]

    return output


def score_sent(data):
    raw = 0
    for item in data["actual"]:
        for i, val in enumerate(data["actual"][item]):
            mod = (i%3)+1
            if mod == 3:
                mod = 10
            raw += mod*val
    return raw



#data = rank_one_sentence(sample)
#print(json.dumps(data, indent=4))
#print(score_sent(data))

#data = rank_one_sentence(sample2)
#print(json.dumps(data, indent=4))
#print(score_sent(data))
no_phonetic_words = []

def clean_sent_for_phonetics(sent):
    sent = list(sent)
    sent2 = []
    global no_phonetic_words
    global viable_words
    for word in sent:
        if rdist.check_phonetic_existance(word):
            sent2.append(word)
        elif word not in no_phonetic_words and word in viable_words:
            no_phonetic_words.append(word)

    return sent2


def try_it_out():
    scores = []
    print("ASD")
    with open("sample_sentences.json") as f:
        data = json.load(f)["sents"]
    for sent in data:
        d = rank_one_sentence(sent)
        score = score_sent(d)
        scores.append(score)
        if score > 40:
            #print("GOOD")
            print(sent)
            #print(rank_one_sentence(sent)['actual'])
            # print()
        # if score < 10:
        #     print("BAD")
        #     print(sent)
        #     print()
    print(scores)

#try_it_out()

def textual_analysis(spec1, spec2, spec3, category, intra):
    """
    :param spec1: this is the base measurement we are accepting as a match, the lowest, like 0.5
    :param spec2: this is the second measurement we are accepting as a match, the medium value, like 0.75
    :param spec3: this is the third measurement we are accepting as a match, the largest value, like 0.9
    :param category: a string, it should be r for rhyme, m for meaning, a for alliteration, v for vowel sound,
                    and
    :param in_or_out: a string, either i for in or in, o for out or out, stands for intra-comparisons and extra-sentence comparison
    :return:
    """
    global no_phonetic_words, model
    sent_array = get_all_sentence_array()
    if spec1 is None:
        spec1 = 0.5
    if spec2 is None:
        spec2 = 0.75
    if spec3 is None:
        spec3 = 0.9

    s1, s2, s3 = spec1, spec2, spec3
    spec1, spec2, spec3 = str(spec1)+ " match",str(spec2)+ " match",str(spec3)+ " match",
    params = [spec1, spec2, spec3]
    #determines whether we consider every word in a sentence or just the unique ones
    unique = False
    phonetics = False
    if category is "r":
        category = "rhyme"
        phonetics = True
    elif category is "ss":
        category = "start-sound"
        phonetics = True
    elif category is "m":
        category = "meaning"
        unique = True
    elif category is "v":
        category = "assonance"

    category_match = category + "_match"
    corpus = {
        category_match: {
                spec1: {

                },
                spec2: {

                },
                spec3: {

                }
        },
        #number of times each individual word i appears in sentence of length n
        "word_list":{

        },
        #num sentences of length n
        "sent_count": {

        },
        #number of unique comparisons between two words
        "comp_count": {

        }
    }

    for i, sent in enumerate(sent_array):
        print(i)
        #print(no_phonetic_words)
        #   INTRA SENTENCE
        #   INTRA SENTENCE
        #   INTRA SENTENCE
        if intra:
            #check to see sentence is valid length
            if len(sent) > 2 and len(sent) < 13:

                if phonetics:
                    sent = clean_sent_for_phonetics(sent)

                #Check uniqueness only if category is related to meaning or rhymes
                if unique:
                    # get list of unique words in sent
                    unique_sent = get_unique_words([sent])[0]
                    l = len(get_unique_words([sent])[0])
                    l_s = str(l) #length string

                else:
                    unique_sent = sent
                    l = len(sent)
                    # l_s stand for and is length_string, used for JSON purposes
                    l_s = str(l)

                # check existence of and increment number of sentences
                if l_s not in corpus['sent_count']:
                    corpus['sent_count'][l_s] = 0
                corpus['sent_count'][l_s] += 1

                #This breaks down our sentences into individual words
                for j, word in enumerate(unique_sent):
                    #this part does basic information about sentences and invidual words, not with word comaparisons
                        #print(word)

                        # existence check for individual words and sentences of said words
                        # ex: "the dog was in the park"  dog is found in a sentence of length 6 so increment count
                        if word not in corpus["word_list"]:
                            corpus["word_list"][word] = create_entry(params)
                        if l_s not in corpus["word_list"][word]["sent_count"]:
                            corpus["word_list"][word]["sent_count"][l_s] = 0
                        corpus["word_list"][word]["sent_count"][l_s] += 1


                # this part does comparisons between words in a sentence
                for j, word in enumerate(unique_sent):

                        for k, next_word in enumerate(unique_sent):
                            if j != k:
                                if l_s not in corpus["comp_count"]:
                                    corpus['comp_count'][l_s] = 0
                                corpus['comp_count'][l_s] += 1

                                similarity = calculate_similarity(word, next_word, category)

                                if l_s not in corpus["word_list"][word]["comp_count"]:
                                    corpus["word_list"][word]["comp_count"][l_s] = 0
                                corpus["word_list"][word]["comp_count"][l_s] +=1
                                if l_s not in corpus["word_list"][next_word]["comp_count"]:
                                    corpus["word_list"][next_word]["comp_count"][l_s] = 0
                                corpus["word_list"][next_word]["comp_count"][l_s] += 1

                                #print("WORD1: {}   WORD2: {}   SIMILARITY: {}".format(word, next_word, str(similarity)))
                                #we check if the comparison is greater than 3 different threshold values, and if so,
                                #we increment the number of total matches, and the number of matches found in both
                                #the first and second word being compared

                                if similarity >= s1:
                                    if l_s not in corpus[category_match][spec1]:
                                        corpus[category_match][spec1][l_s] = 0
                                    corpus[category_match][spec1][l_s]  += 1

                                    if l_s not in corpus["word_list"][word][spec1]:
                                        corpus["word_list"][word][spec1][l_s] = 0
                                    corpus["word_list"][word][spec1][l_s] +=1

                                    if l_s not in corpus["word_list"][next_word][spec1]:
                                        corpus["word_list"][next_word][spec1][l_s] = 0
                                    corpus["word_list"][next_word][spec1][l_s] +=1

                                if similarity >= s2:
                                    if l_s not in corpus[category_match][spec2]:
                                        corpus[category_match][spec2][spec2] = 0
                                    corpus[category_match][spec2][spec2] += 1

                                    if l_s not in corpus["word_list"][word][spec2]:
                                        corpus["word_list"][word][spec2][l_s] = 0
                                    corpus["word_list"][word][spec2][l_s] += 1

                                    if l_s not in corpus["word_list"][next_word][spec2]:
                                        corpus["word_list"][next_word][spec2][l_s] = 0
                                    corpus["word_list"][next_word][spec2][l_s] += 1

                                if similarity >= s3:
                                    if l_s not in corpus[category_match][spec3]:
                                        corpus[category_match][spec3][l_s] = 0
                                    corpus[category_match][spec3][l_s] += 1

                                    if l_s not in corpus["word_list"][word][spec3]:
                                        corpus["word_list"][word][spec3][l_s] = 0
                                    corpus["word_list"][word][spec3][l_s] += 1

                                    if l_s not in corpus["word_list"][next_word][spec3]:
                                        corpus["word_list"][next_word][spec3][l_s] = 0
                                    corpus["word_list"][next_word][spec3][l_s] += 1


        else:
            #   EXTRA SENTENCE
            #   EXTRA SENTENCE
            #   EXTRA SENTENCE

            if len(sent) > 2 and len(sent) < 13 and i < len(sent_array) - 2 and len(sent_array[i + 1]) > 2 and len(
                    sent_array[i + 1]) < 13:
                q = i + 1

                next_sent = sent_array[q]
                #print(sent)

                if phonetics:
                    sent = clean_sent_for_phonetics(sent)
                    next_sent = clean_sent_for_phonetics(next_sent)

                #print(next_sent)
                # Check uniqueness only if category is related to meaning or rhymes
                if unique:
                    # get list of unique words in sent
                    unique_sent = get_unique_words([sent])[0]
                    unique_sent2 = get_unique_words([sent])[0]
                    l = len(unique_sent2)
                    # l_s stand for and is length_string, used for JSON purposes
                    l_s = str(l)
                    next_sent = get_unique_words([next_sent])[0]
                    next_sent2 = next_sent[0]
                    l_2 = str(len(next_sent2))
                else:
                    unique_sent = sent
                    unique_sent2 = sent
                    next_sent2 = next_sent
                    l = len(sent)
                    # l_s stand for and is length_string, used for JSON purposes
                    l_s = str(l)
                    l_2 = str(len(next_sent))
                # increment number of sentences
                if l_s not in corpus['sent_count']:
                    corpus['sent_count'][l_s] = 0
                corpus['sent_count'][l_s] += 1

                for word in unique_sent:

                    # this part does basic information about sentences and invidual words, not with word comaparisons
                        #print(word)
                        # existence check
                        if word not in corpus["word_list"]:
                            corpus["word_list"][word] = create_entry(params)
                        if l_s not in corpus["word_list"][word]["sent_count"]:
                            corpus["word_list"][word]["sent_count"][l_s] = 0
                        corpus["word_list"][word]["sent_count"][l_s] += 1


                        l_s = str(len(unique_sent2) + len(next_sent2))

                    # this part does comparisons between words in two sentences

                        # compare jth word to all of the other k's

                        for next_word in next_sent2:
                            #print(next_word)
                            if l_s not in corpus["comp_count"]:
                                corpus['comp_count'][l_s] = 0
                            corpus['comp_count'][l_s] += 1

                            similarity = calculate_similarity(word, next_word, category)

                            if l_s not in corpus["word_list"][word]["comp_count"]:
                                corpus["word_list"][word]["comp_count"][l_s] = 0
                            if next_word not in corpus["word_list"]:
                                corpus["word_list"][next_word] = create_entry(params)
                            corpus["word_list"][word]["comp_count"][l_s] += 1
                            if l_s not in corpus["word_list"][next_word]["comp_count"]:
                                corpus["word_list"][next_word]["comp_count"][l_s] = 0
                            corpus["word_list"][next_word]["comp_count"][l_s] += 1
                            # print("WORD1: {}   WORD2: {}   SIMILARITY: {}".format(word, next_word, str(similarity)))
                            # we check if the comparison is greater than 3 different threshold values, and if so,
                            # we increment the number of total matches, and the number of matches found in both
                            # the first and second word being compared

                            if similarity >= s1:
                                if l_s not in corpus[category_match][spec1]:
                                    corpus[category_match][spec1][l_s] = 0
                                corpus[category_match][spec1][l_s]  += 1

                                if l_s not in corpus["word_list"][word][spec1]:
                                    corpus["word_list"][word][spec1][l_s] = 0
                                corpus["word_list"][word][spec1][l_s] +=1

                                if l_s not in corpus["word_list"][next_word][spec1]:
                                    corpus["word_list"][next_word][spec1][l_s] = 0
                                corpus["word_list"][next_word][spec1][l_s] +=1

                            if similarity >= s2:
                                if l_s not in corpus[category_match][spec2]:
                                    corpus[category_match][spec2][spec2] = 0
                                corpus[category_match][spec2][spec2] += 1

                                if l_s not in corpus["word_list"][word][spec2]:
                                    corpus["word_list"][word][spec2][l_s] = 0
                                corpus["word_list"][word][spec2][l_s] += 1

                                if l_s not in corpus["word_list"][next_word][spec2]:
                                    corpus["word_list"][next_word][spec2][l_s] = 0
                                corpus["word_list"][next_word][spec2][l_s] += 1

                            if similarity >= s3:
                                if l_s not in corpus[category_match][spec3]:
                                    corpus[category_match][spec3][l_s] = 0
                                corpus[category_match][spec3][l_s] += 1

                                if l_s not in corpus["word_list"][word][spec3]:
                                    corpus["word_list"][word][spec3][l_s] = 0
                                corpus["word_list"][word][spec3][l_s] += 1

                                if l_s not in corpus["word_list"][next_word][spec3]:
                                    corpus["word_list"][next_word][spec3][l_s] = 0
                                corpus["word_list"][next_word][spec3][l_s] += 1
    print(no_phonetic_words)
    if intra:
        name_of_file = "intra_"
    else:
        name_of_file = "extra_"
    name_of_file += category
    name_of_file += "_corp.json"
    print(name_of_file)
    with open(name_of_file, 'w') as outfile:
        json.dump(corpus, outfile, indent=4)
    pass



#textual_analysis(0.5,0.6,0.7, "r", True)
