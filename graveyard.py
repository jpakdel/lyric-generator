#This file contains all the functions that are now defunct
#That I did not have the heart to delete.  RIP 

def create_last_word_chains():
    """
    Used to create unique markov chains for words that are found at the end of sentences and are considered to be viable
    """
    song_urls = lyricsorter.get_song_url_list()
    word_list = []
    word_dict = {}
    Item = {}
    Item['id'] = "last_words"
    Item['words'] = {}
    viable_words = find_viable_words()
    for i, link in enumerate(song_urls):
        print("Last wording through song #{}".format(str(i)))
        response = song_table.get_item(
            Key={
                'id': link
            }
        )
        lyrics = []
        try:
            lyrics = response['Item']['lyric_array']
        except KeyError:
            pass

        for line in lyrics:
            if len(line) > 2 and len(line) < 12:
                last_word = line[len(line) - 1]
                second_last_word = line[len(line) - 2]
                third_last_word = line[len(line) - 3]
                # print(line)
                if last_word in viable_words and second_last_word in viable_words:
                    if last_word not in word_list:
                        word_list.append(last_word)
                    if last_word not in word_dict:
                        word_dict[last_word] = {
                            "1": {

                            },
                            "2": {

                            }
                        }
                    if second_last_word not in word_dict[last_word]["1"]:
                        word_dict[last_word]["1"][second_last_word] = 1
                    else:
                        word_dict[last_word]["1"][second_last_word] = word_dict[last_word]["1"][second_last_word] + 1
                    if third_last_word in viable_words:
                        if third_last_word not in word_dict[last_word]["2"]:
                            word_dict[last_word]["2"][third_last_word] = 1
                        else:
                            word_dict[last_word]["2"][third_last_word] = word_dict[last_word]["2"][third_last_word] + 1

    # print(word_dict)
    for i, word in enumerate(word_list):
        # print("Inserting word #{} of {}".format(str(i), str(len(word_list))))
        label_1 = str(word + "_last1")
        label_2 = str(word + "_last2")
        item1 = {
            "id": label_1,
            "words": word_dict[word]["1"]
        }
        item2 = {
            "id": label_2,
            "words": word_dict[word]["2"]
        }
        word_relation_table.put_item(
            Item=item1
        )
        word_relation_table.put_item(
            Item=item2
        )


def build_sentence(length: int, input=None):
    """
    Primary function used to generate rap lyrics
    :param length: length of sentence, must be >= 3
    :param input: word you want to use at the end of a sentence, if not given then random word is chosen
    """
    global other_time, database_time
    # print(other_time)
    # print(database_time)
    # print()
    while True:
        start = time.time()
        try:
            last_word = __choose_last_word()
            sentence = []
            i = 0
            while i < length:
                sentence.append("")
                i += 1

            if input != None:
                last_word = input

            # start of the sentence
            sentence[length - 1] = last_word

            # find markov data from last word
            a = get_relation_dict(last_word, -1)

            second_to_last_word = __probability_roll(a)
            sentence[length - 2] = second_to_last_word
            i = length - 3
            while i >= 0:
                word_1 = sentence[i + 2]
                word_2 = sentence[i + 1]

                # words 2 steps away and one step away respectively
                prev_words_2 = get_relation_dict(word_1, 2)
                prev_words_1 = get_relation_dict(word_2, 1)
                prev_word_list = [prev_words_1, prev_words_2]

                if (i + 3) < length:
                    word_0 = sentence[i + 3]
                    prev_words_3 = get_relation_dict(word_0, 3)
                    prev_word_list.append(prev_words_3)

                if (i + 4) < length:
                    word_00 = sentence[i + 4]
                    prev_words_4 = get_relation_dict(word_00, 4)
                    prev_word_list.append(prev_words_4)

                try:
                    # print(sentence)
                    potential_words = __find_union(prev_word_list)
                    # print(len(potential_words))
                    sentence[i] = __probability_roll(potential_words)
                    j = 0
                    while j < 3:
                        # print("sentence i, i+1: {}, {}".format(sentence[i],sentence[i+1]))
                        if sentence[i] == sentence[1 + 1]:
                            sentence[i] = __probability_roll(potential_words)
                        j += 1
                    # print("Union of {} spaces".format(str(len(prev_word_list))))
                except IndexError:
                    sentence[i] = __probability_roll(prev_words_1)
                    # print("Dice  Roll")
                i -= 1
            duplicate_count = count_duplicates(sentence)
            if duplicate_count > 0:
                raise ValueError
            print(sentence)
            return (sentence)
        except KeyError:
            print("keyerror")
            print(sentence)

        except TypeError:
            print("typeERROR")
        except ValueError:
            print("too many duplicates")


def __line_parse_4(index: int, line: list, dictionary: dict, word_list: list):
    """
    Helper method for parsing sentences to create markov chains of length 4
    :param index: of word we want to build chain of
    :param line: list of words, our sentence
    :param dictionary: of markov relations
    :param word_list: list of words
    :return:
    """
    if index + 4 >= len(line):
        return
    word_1 = line[index + 4]
    word_2 = line[index + 3]
    word_3 = line[index + 2]
    word_4 = line[index + 1]
    word_5 = line[index]

    if word_1 == "" or word_2 == "" or word_3 == "" or word_4 == "" or word_5 == "":
        return

    if word_1 not in dictionary:
        dictionary[word_1] = {
            str(word_1 + "_4"): {

            }
        }
    if word_1 not in word_list:
        word_list.append(word_1)

    """word_5     word_4     word_3      word_2     word_1"""
    if word_5 not in dictionary[word_1][str(word_1 + "_4")]:
        dictionary[word_1][str(word_1 + "_4")][word_5] = 1
    else:
        dictionary[word_1][str(word_1 + "_4")][word_5] = dictionary[word_1][str(word_1 + "_4")][word_5] + 1


def build_word_relations_4():
    """
    Builds markov chain relations of size length 4
    :return:
    """
    song_urls = lyricsorter.get_song_url_list()
    viablewords = find_viable_words()
    word_list = []
    relation_dict = {}

    for i, link in enumerate(song_urls):
        print("parsing through song #{}".format(str(i)))
        response = song_table.get_item(
            Key={
                'id': link
            }
        )
        lyrics = []
        try:
            lyrics = response['Item']['lyric_array']
        except KeyError:
            pass
        for index, line in enumerate(lyrics):
            for index2, w in enumerate(line):
                if w not in viablewords:
                    lyrics[index][index2] = ""
        for index, line in enumerate(lyrics):
            for index2, w in enumerate(line):
                __line_parse_4(index2, line, relation_dict, word_list)

    print(len(word_list))
    for i, word in enumerate(word_list):
        print("inserting word #{} of {}".format(str(i), str(len(word_list))))
        Item = {
            'id': str(word + "_4"),
            "words": relation_dict[word][str(word + "_4")]
        }
        word_relation_table.put_item(
            Item=Item
        )
        print("added {}".format(word))


def __find_union(dicts: list):
    """
    Find union of a list of dictionaries and return those values in a new dictionary
    """
    global other_time
    start = time.time()
    union_list = []
    while len(dicts) > 1:
        word_count = {}
        final_dict = {}
        for d in dicts:
            # print(json.dumps(d, indent=4))
            for word in d:
                if word not in word_count:
                    word_count[word] = 1
                else:
                    word_count[word] = word_count[word] + 1
        for item in word_count:
            if word_count[item] == len(dicts):
                union_list.append(item)
        for d in dicts:
            for word in d:
                if word in union_list:
                    if word not in final_dict:
                        final_dict[word] = d[word]
                    else:
                        final_dict[word] += d[word]
        if len(final_dict) > 0:
            # print(len(dicts))
            end = time.time()
            diff = end - start
            other_time += diff
            # print(json.dumps(final_dict, indent=4))
            return (final_dict)
        else:

            dicts = dicts[:len(dicts) - 1]

    end = time.time()
    diff = end - start
    other_time += diff
    return {}


def get_relation_dict(word: str, num: int):
    """
    Get markov chains of length=num and word=word
    :return: dictionary of markov chains
    """
    global database_time, other_time
    label = str(word + "_" + str(num))

    # These two cases are used in finding relations of "last" words, words we find at the end of a sentence
    if num == -1:
        label = str(word + "_last1")
    elif num == -2:
        label = str(word + "_last2")

    start = time.time()

    # response = word_relation_table.get_item(
    #     Key = {
    #         "id": label
    #     }
    # )

    end = time.time()
    diff = end - start
    database_time += diff
    # data = response['Item']['words']
    data = word_relation_lookup(label)
    start = time.time()

    data1 = __clean_noise(data, 0.0025)
    if __get_json_sum(data1) == 0:
        data1 = __clean_noise(data, 0.00125)
        print("switchin it up")
    if __get_json_sum(data1) == 0:
        print("switchin it up11111")
        data1 = data

    end = time.time()
    diff = end - start
    other_time += diff
    return dict(data1)


def __clean_noise(data, tuning):
    sum = __get_json_sum(data)
    out_data = {}
    for item in data:
        # print(item)
        # print(data[item])
        # print(sum)
        probability = float(data[item] / sum)
        # print(probability)
        # print()

        if probability > tuning:
            if item == "i" or item == "you" or item == "me" or item == "and":
                probability = probability / 2
            out_data[item] = 100 * probability
    return out_data


def __probability_roll(dictionary: dict):
    """
    Given a dictionary of markov relations and probability, returns a word based on probability of its previous
    occurence
    :param dictionary: of markov relations
    :return: pseudo-random word chosen
    """
    global other_time
    start = time.time()
    sum = 0
    word_list = []

    randint = 0
    # print(dictionary)
    for item in dictionary:
        if len(dictionary) == 1:
            end = time.time()
            diff = end - start
            other_time += diff
            return item
        word_list.append(item)
        sum += int(dictionary[item])
    if sum > 1:
        randint = random.randint(1, sum)
    else:
        randit = 1
    dice = 0
    # print("randint: {}".format(randint))
    for word in word_list:
        dice += int(dictionary[word])
        # print(dice)
        if dice >= randint:
            end = time.time()
            diff = end - start
            other_time += diff
            return word


def build_word_relations():
    """
    builds markov chains of length 1 2 and 3 of all songs in the database
    :return:
    """
    song_urls = lyricsorter.get_song_url_list()
    viablewords = find_viable_words()
    word_list = []
    relation_dict = {}
    for i, link in enumerate(song_urls):
        response = song_table.get_item(
            Key={
                'id': link
            }
        )
        lyrics = []
        print("Working on song# {}".format(str(i)))
        try:
            lyrics = response['Item']['lyric_array']
        except KeyError:
            pass
        for index, line in enumerate(lyrics):
            for index2, w in enumerate(line):
                if w not in viablewords:
                    lyrics[index][index2] = ""
        for index, line in enumerate(lyrics):
            for index2, w in enumerate(line):
                __line_parse(index2, line, relation_dict, word_list)

    for i, word in enumerate(word_list):
        print("Inserting #{} word in wordlist of size {}".format(str(i), str(len(word_list))))
        Item1 = {
            'id': str(word + "_1"),
            "words": relation_dict[word][str(word + "_1")]
        }
        Item2 = {
            'id': str(word + "_2"),
            "words": relation_dict[word][str(word + "_2")]
        }
        Item3 = {
            'id': str(word + "_3"),
            "words": relation_dict[word][str(word + "_3")]
        }
        word_relation_table.put_item(
            Item=Item1
        )
        word_relation_table.put_item(
            Item=Item2
        )
        word_relation_table.put_item(
            Item=Item3
        )


def __line_parse(index: int, line: list, dictionary: dict, word_list: list):
    """
    Parses a sentence to build markov chains of length 1 2 and 3
    :param index: of word we want to build relations of
    :param line: list of words, our sentence
    :param dictionary: of markov chains
    :param word_list: list of words we have
    :return:
    """

    if index + 2 >= len(line):
        return
    word_1 = line[index + 2]
    word_2 = line[index + 1]
    word_3 = line[index]
    if word_1 == "" or word_2 == "" or word_3 == "":
        return

    if word_1 not in dictionary:
        dictionary[word_1] = {
            str(word_1 + "_1"): {

            },
            str(word_1 + "_2"): {

            },
            str(word_1 + "_3"): {

            }
        }
    if word_2 not in dictionary:
        dictionary[word_2] = {
            str(word_2 + "_1"): {

            },
            str(word_2 + "_2"): {

            },
            str(word_2 + "_3"): {

            }
        }
    if word_3 not in dictionary:
        dictionary[word_3] = {
            str(word_3 + "_1"): {

            },
            str(word_3 + "_2"): {

            },
            str(word_3 + "_3"): {

            }
        }
    if word_1 not in word_list:
        word_list.append(word_1)
    if word_2 not in word_list:
        word_list.append(word_2)
    if word_3 not in word_list:
        word_list.append(word_3)
    """         word_3       word_2     word_1"""
    if word_2 not in dictionary[word_1][str(word_1 + "_1")]:
        dictionary[word_1][str(word_1 + "_1")][word_2] = 1
    else:
        dictionary[word_1][str(word_1 + "_1")][word_2] = dictionary[word_1][str(word_1 + "_1")][word_2] + 1
    if word_3 not in dictionary[word_1][str(word_1 + "_2")]:
        dictionary[word_1][str(word_1 + "_2")][word_3] = 1
    else:
        dictionary[word_1][str(word_1 + "_2")][word_3] = dictionary[word_1][str(word_1 + "_2")][word_3] + 1
    if word_3 not in dictionary[word_2][str(word_2 + "_1")]:
        dictionary[word_2][str(word_2 + "_1")][word_3] = 1
    else:
        dictionary[word_2][str(word_2 + "_1")][word_3] = dictionary[word_2][str(word_2 + "_1")][word_3] + 1
    if index + 3 >= len(line) or line[index + 3] == "":
        return
    word_0 = line[index + 3]
    if word_0 not in dictionary:
        dictionary[word_0] = {
            str(word_0 + "_1"): {

            },
            str(word_0 + "_2"): {

            },
            str(word_0 + "_3"): {

            }
        }

    if word_0 not in word_list:
        word_list.append(word_0)

    if word_3 not in dictionary[word_0][str(word_0 + "_3")]:
        dictionary[word_0][str(word_0 + "_3")][word_3] = 1
    else:
        dictionary[word_0][str(word_0 + "_3")][word_3] = dictionary[word_0][str(word_0 + "_3")][word_3] + 1


def create_last_word_dict():
    """
    scans through all song lyrics and creates dict of words found at the end of sentences
    """
    song_urls = get_song_url_list()
    word_dict = {}

    lyrics = get_all_sentence_array()
    viable_words = find_viable_words()
    for i, line in enumerate(lyrics):
        print(i)
        if len(line) > 2 and len(line) < 12:
            last_word = line[0]
            if last_word in viable_words:
                if last_word not in word_dict:
                    word_dict[last_word] = 1
                else:
                    word_dict[last_word] = word_dict[last_word] + 1

    with open('first_word_dict.json', 'w') as outfile:
        json.dump(word_dict, outfile, indent=4)
