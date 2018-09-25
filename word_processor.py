import helper_methods
import slang_cleaner
import scraper
import boto3
import random
from lyricsorter import get_song_url_list, hasNumbers, remove_paranthases
dynamodb = boto3.resource("dynamodb")
proxy_table = dynamodb.Table("Proxy")
word_table = dynamodb.Table("Word")
word_relation_table = dynamodb.Table("WordRelation")
song_table = dynamodb.Table("Song")


def get_word_list():
    """
    Returns list and dict of all words in database
    """
    raw_words = list(word_table.scan()['Items'])
    word_list = []
    word_dict = {}
    word_dict_unsorted = {}
    for item in raw_words:
        word_list.append(str(item.get("id")))
        try:
            word_dict_unsorted[str(item.get("id"))] = {"num_occurrences": int(item['num_occurrences']),
                                                        "slang": item['slang']}
        except TypeError:
            word_dict_unsorted[str(item.get("id"))] = {"num_occurrences": int(item['num_occurrences']),
                                                        "slang": item['slang']}
            pass
    word_list = sorted(word_list)

    for item in word_list:
        word_dict[item] = word_dict_unsorted[item]
    return [word_list, word_dict]

def fill_word_dict(x: int, y: int):
    """Uses a song url to look up the lyrics and get all the individual words from them"""
    song_urls = get_song_url_list()
    words = get_word_list()
    word_list = words[0]
    word_dict = words[1]

    while x < y:
        if x > len(song_urls) - 1:
            break
        link = song_urls[x]
        x += 1
        response = song_table.get_item(
            Key={
                'id': link
            }
        )

        item = response['Item']
        lyrics = str(item['lyrics'])
        lyric_list = lyrics.split("\n")

        output_list = []
        print(link)
        for item in lyric_list:
            # Take  out the punctuation
            item = item.replace("?", "")
            item = item.replace(",", "")
            item = item.replace(".", " ")
            item = item.replace("\"", "")
            item = item.replace("-", " ")
            item = item.replace("!", "")
            item = item.lower()

            # We only want the line if it doesn't have numbers, and doesn't have a colon, which means its not actual lyrics
            if item not in output_list and hasNumbers(item) is False and scraper.contains(item, ":") is False:
                output_list.append(remove_paranthases(item).strip())

        for item in output_list:
            word_lines = item.split(" ")
            # we only want sentences with more than three words, because some of the text in the lyrics aren'tactual song lyrics
            # and we want to avoid adding those
            if len(word_lines) > 3:
                for word in word_lines:
                    word = str(word).lower()

                    # make sure we aren't adding html code
                    if len(word) > 0 and scraper.contains(word, "&") is False:
                        if word[0] == '\'':
                            word = word[1:len(word)]

                        # replace slang words with their real equivalent\
                        word = slang_cleaner.remove_weirdness(word)
                        slang_word = slang_cleaner.clean_misspellings(word)
                        word = slang_cleaner.clean_slang(slang_word)
                        if word in word_list:
                            num_occurrences = int(word_dict[word]["num_occurrences"]) + 1
                            word_dict[word]["num_occurrences"] = num_occurrences
                            if link not in word_dict[word]["songs"]:
                                word_dict[word]["songs"].append(link)
                            if word != slang_word and slang_word not in word_dict[word]["slang"]:
                                word_dict[word]["slang"].append(slang_word)
    for word in word_list:
        print(word)
        helper_methods.update_table(word_table, word, "num_occurrences", int(word_dict[word]["num_occurrences"]))
        helper_methods.update_table(word_table, word, "slang", word_dict[word]["slang"])


def setup_word_table():
    """Initializes the number of occurrences, songs words are found in, and slang deriviatives of all the words in the
    dyanmodb word table"""
    words = get_word_list()
    word_list = words[0]
    for word in word_list:
        print(word)
        helper_methods.update_table(word_table, word, "num_occurrences", 0 )
        helper_methods.update_table(word_table, word, "slang", [])
        helper_methods.update_table(word_table, word, "songs", [])

def __reformat_word_table():
    """removes song attribute from all the words"""
    raw_words = list(word_table.scan()['Items'])

    for word in raw_words:
        Item = {'id': word['id'], 'num_occurrences': word['num_occurrences'], 'slang': word['slang']}
        word_table.put_item(
            Item=Item
        )
        print(Item)


def find_nonviable_words():
    """
    Returns list of words we have found only once 
    """
    response = get_word_list()
    word_list = response[0]
    word_dict = response[1]
    nonviableset = []
    non_viable_words = 0

    numa = 0
    for word in word_list:
        if  word_dict[word]['num_occurrences'] > 1:
            pass
        else:
            non_viable_words+=1
            nonviableset.append(word)



    return(nonviableset)

def find_viable_words():
    """
    Returns list and dict of words we have found more than one time in song lyrics
    """
    response = get_word_list()
    word_list = response[0]
    word_dict = response[1]
    viableset = []
    viable_words = 0

    numa = 0
    for word in word_list:
        if  word_dict[word]['num_occurrences'] > 1:
            viable_words += 1
            viableset.append(word)
        else:
            pass
    return(viableset)


def find_word(words):
    """
    Scans through entire song lyrics to find which song and line they are found in
    :param words: 
    :return: 
    """
    song_urls = get_song_url_list()
    for link in song_urls:
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
            for w in line:
                for word in words:
                    if word == w:
                        print(word)
                        print(link)
                        print(line)


word_fixes = {
    "nu": "new",
    "dis": "this",
    "ta": "the",
    "lames": "bitches",
    "skrip": "strip",
    "krazy": "crazy",
    "caucasians": "white",
    "nike's": "nikes",
    "he's": "he",
    "she's":"she",
    "ova":"over",
    "skees": "skis",
    "politicians": "politician",
    "caucasian": "white",
    "boy's": "boys",
    "cha": "your",
    "grandaddy": "granddaddy",
    "quarantined": "quarantine",
    "em": "them",
    "hansom": "handsome",
    "girlfriend's": "girlfriend",
    "thoughta": "thought",
    "robed": "robbed",
    "wit": "with",
    "girly": "girl",
    "cuss": "cause",
    "girlfriends": "girlfriend",
    "sho": "sure",
    "wanner": "wanna",
    "kats": "cats",
    "jury's": "jury",
    "eww": "ew",
    "officers": "cops",
    "phallus": "cock",
    "baddies": "bad",
    "fuzz": "cops",
    "kemosabe": "kimosabe",
    "neighbor's": "neighbor",
    "asses": "ass",
    "jewerly's": "jewerly",
    "jetskis": "skis",
    "gwaluh": "guala",
    "deers": "deer",
    "aah": "ah"
}
def replace_words(words):
    """
    given a dict of words and their replacements, replaces those words in the song lyrics
    :param words: dict of words and replacements
    """
    song_urls = get_song_url_list()
    for link in song_urls:
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
            for index, w in enumerate(line):

                if w in words:
                    print(w)
                    fix = words[w]
                    print(fix)
                    response = word_table.get_item(
                        Key = {
                            'id': fix
                        }
                    )
                    if 'Item' in response:
                        num_occurrences = response["Item"]['num_occurrences']
                        print(link)
                        print(line)
                        helper_methods.update_table(word_table, fix, "num_occurrences", (num_occurrences+1))
                        line[index] = fix
                        print(line)
                        helper_methods.update_table(song_table, link, "lyric_array", lyrics)

def create_last_word_dict():
    """
    scans through all song lyrics and creates dict of words found at the end of sentences 
    """
    song_urls = get_song_url_list()
    word_list = []
    word_dict = {}
    Item = {}
    Item['id'] = "last_words"
    Item['words'] = {}
    for link in song_urls:
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
            if len(line) > 2:
                last_word = line[len(line)-1]
                print(line)
                if last_word not in word_list:
                    word_list.append(last_word)
                if last_word not in word_dict:
                    word_dict[last_word] = 1
                else:
                    word_dict[last_word] = word_dict[last_word] + 1

    viable_words = find_viable_words()
    for word in sorted(word_list):
        if word in viable_words:
            Item['words'][word] = word_dict[word]
    word_relation_table.put_item(
        Item=Item
    )
    print(Item)

def __choose_last_word():
    """
    randomly returns a word from list of words we have found at the end of sentences
    """
    response = word_relation_table.get_item(
        Key = {
            'id': "last_words"
        }
    )
    last_words = dict(response['Item']['words'])
    total = 26124
    randint = random.randint(0,total)

    sum = 0
    for word in last_words:
        sum += last_words[word]
        if sum >= randint:
            return word

def __probability_roll(dictionary: dict):
    """
    Given a dictionary of markov relations and probability, returns a word based on probability of its previous
    occurence
    :param dictionary: of markov relations
    :return: pseudo-random word chosen
    """
    sum = 0
    word_list = []
    for item in dictionary:
        if len(dictionary)==1:
            return item
        word_list.append(item)
        sum+=int(dictionary[item])
    if sum != 1:
        randint = random.randint(1, sum)
    else:
        randit = 1
    dice = 0
    #print("randint: {}".format(randint))
    for word in word_list:
        dice+=int(dictionary[word])
        #print(dice)
        if dice >= randint:
            return word
        
def build_word_relations():
    """
    builds markov chains of length 1 2 and 3 of all songs in the database
    :return: 
    """
    song_urls = get_song_url_list()
    viablewords = find_viable_words()
    word_list = []
    relation_dict = {}
    for link in song_urls:
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
                __line_parse(index2, line, relation_dict, word_list)

    for word in word_list:
        Item1 = {
            'id': str(word+"_1"),
            "words": relation_dict[word][str(word+"_1")]
        }
        Item2 = {
            'id': str(word + "_2"),
            "words": relation_dict[word][str(word+"_2")]
        }
        Item3 = {
            'id': str(word + "_3"),
            "words": relation_dict[word][str(word+"_3")]
        }
        word_relation_table.put_item(
            Item = Item1
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
        dictionary[word_1][str(word_1 + "_1")][word_2] =dictionary[word_1][str(word_1 + "_1")][word_2]+1
    if word_3 not in dictionary[word_1][str(word_1 + "_2")]:
        dictionary[word_1][str(word_1 + "_2")][word_3] = 1
    else:
        dictionary[word_1][str(word_1 + "_2")][word_3] =dictionary[word_1][str(word_1 + "_2")][word_3]+1
    if word_3 not in dictionary[word_2][str(word_2 + "_1")]:
        dictionary[word_2][str(word_2 + "_1")][word_3] = 1
    else:
        dictionary[word_2][str(word_2 + "_1")][word_3] = dictionary[word_2][str(word_2 + "_1")][word_3]+1
    if index + 3 >= len(line) or line[index+3] == "":
        return
    word_0 = line[index+3]
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
        dictionary[word_0][str(word_0 + "_3")][word_3] = dictionary[word_0][str(word_0 + "_3")][word_3]+1

def check_exists(id):
    response = word_relation_table.get_item(
        Key={
            "id": id
        }
    )
    if 'Item' in response:
        print(id + " exists")
        return True
    else:
        print(id + " doesn't exist")
        return False

def get_relation_dict(word: str, num: int):
    """
    Get markov chains of length=num and word=word
    :return: dictionary of markov chains
    """
    label = str(word+"_"+str(num))

    #These two cases are used in finding relations of "last" words, words we find at the end of a sentence
    if num == -1:
        label = str(word + "_last1")
    elif num == -2:
        label = str(word + "_last2")

    response = word_relation_table.get_item(
        Key = {
            "id": label
        }
    )
    if num < 0 and 'Item' not in response:
        label = str(word + "_1")
        response = word_relation_table.get_item(
            Key = {
                "id": label
            }
        )
    return dict(response['Item']['words'])

def __find_union(dicts: list):
    """
    Find union of a list of dictionaries and return those values in a new dictionary
    """
    union_list = []
    while len(dicts)>1:
        word_count = {}
        final_dict = {}
        for d in dicts:
            for word in d:
                if word not in word_count:
                    word_count[word] = 1
                else:
                    word_count[word]=word_count[word]+1
        for item in word_count:
            if word_count[item] == len(dicts):
                union_list.append(item)
        for d in dicts:
            for word in d:
                if word in union_list:
                    if word not in final_dict:
                        final_dict[word]=d[word]
                    else:
                        final_dict[word]+=d[word]
        if len(final_dict) >0:
            return (final_dict)
        else:

            dicts = dicts[:len(dicts)-1]


    return {}


def build_sentence(length: int, input=None):
    """
    Primary function used to generate rap lyrics
    :param length: length of sentence, must be >= 3
    :param input: word you want to use at the end of a sentence, if not given then random word is chosen
    """
    last_word = __choose_last_word()
    sentence = []
    i = 0
    while i < length:
        sentence.append("")
        i += 1

    if input != None:
        last_word = input
    sentence[length - 1] = last_word
    a = get_relation_dict(last_word, -1)
    #print(a)
    second_to_last_word = __probability_roll(a)
    #print(second_to_last_word)
    sentence[length - 2] = second_to_last_word
    i = length-3
    while i>=0:
        word_1=sentence[i+2]
        word_2 =sentence[i+1]

        #words 2 steps away and one step away respectively
        prev_words_2 = get_relation_dict(word_1, 2)
        prev_words_1 = get_relation_dict(word_2, 1)
        prev_word_list = [prev_words_1, prev_words_2]

        if(i+3)<length:
            word_0 = sentence[i+3]
            prev_words_3 = get_relation_dict(word_0, 3)
            prev_word_list.append(prev_words_3)

        if (i + 4) < length:
            word_00 = sentence[i + 4]
            prev_words_4 = get_relation_dict(word_00, 4)
            prev_word_list.append(prev_words_4)

        try:
            potential_words = __find_union(prev_word_list)
            #print(len(potential_words))
            sentence[i] = __probability_roll(potential_words)
            #print("Union of {} spaces".format(str(len(prev_word_list))))
        except IndexError:
            sentence[i]=__probability_roll(prev_words_1)
            print("Dice  Roll")
        i-=1
    print(sentence)

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
    word_3 = line[index+2]
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
        dictionary[word_1][str(word_1 + "_4")][word_5] =dictionary[word_1][str(word_1 + "_4")][word_5]+1

def build_word_relations_4():
    """
    Builds markov chain relations of size length 4
    :return:
    """
    song_urls = get_song_url_list()
    viablewords = find_viable_words()
    word_list = []
    relation_dict = {}

    for link in song_urls:
        print(link)
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
    for word in word_list:
        Item = {
            'id': str(word + "_4"),
            "words": relation_dict[word][str(word + "_4")]
        }
        word_relation_table.put_item(
            Item=Item
        )
        print("added {}".format(word))

def create_last_word_chains():
    """
    Used to create unique markov chains for words that are found at the end of sentences and are considered to be viable
    """
    song_urls = get_song_url_list()
    word_list = []
    word_dict = {}
    Item = {}
    Item['id'] = "last_words"
    Item['words'] = {}
    viable_words = find_viable_words()
    for link in song_urls:
        print(link)
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
            if len(line) > 2:
                last_word = line[len(line)-1]
                second_last_word = line[len(line)-2]
                third_last_word = line[len(line)-3]
                #print(line)
                if last_word in viable_words and second_last_word in viable_words:
                    if last_word not in word_list:
                        word_list.append(last_word)
                    if last_word not in word_dict:
                        word_dict[last_word] = {
                            "1":{

                            },
                            "2":{

                            }
                        }
                    if second_last_word not in word_dict[last_word]["1"]:
                        word_dict[last_word]["1"][second_last_word] = 1
                    else:
                        word_dict[last_word]["1"][second_last_word] =word_dict[last_word]["1"][second_last_word] +1
                    if third_last_word in viable_words:
                        if third_last_word not in word_dict[last_word]["2"]:
                            word_dict[last_word]["2"][third_last_word] = 1
                        else:
                            word_dict[last_word]["2"][third_last_word] = word_dict[last_word]["2"][third_last_word] + 1


    print(word_dict)
    for word in word_list:
        print(word)
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
