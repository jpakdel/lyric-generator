#import helper_methods
import numpy as np
import slang_cleaner
#import scraper

import boto3
import random
import json
import lyricsorter
import helper_methods
import time
import botocore
from helper_methods import word_relation_lookup, get_song_url_list, get_all_sentence_array, dprint, jprint
dynamodb = boto3.resource("dynamodb")
proxy_table = dynamodb.Table("Proxy")
lyric_table = dynamodb.Table("Lyric")
lyric_link_table = dynamodb.Table("LyricLink")
word_table = dynamodb.Table("Word")
rhyme_table = dynamodb.Table("Rhyme")
word_relation_table = dynamodb.Table("WordRelation")
song_table = dynamodb.Table("Song")
database_time =0
other_time = 0

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
            word_dict_unsorted[str(item.get("id"))] = item
        except TypeError:
            word_dict_unsorted[str(item.get("id"))] = item
            pass
    word_list = sorted(word_list)

    for item in word_list:
        word_dict[item] = word_dict_unsorted[item]
    return [word_list, word_dict]

def fill_word_dict(x: int, y: int):
    """Uses a song url to look up the lyrics and get all the individual words from them"""
    song_urls = lyricsorter.get_song_url_list()
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
        print(str(x))
        for item in lyric_list:
            # Take  out the punctuation
            item = item.replace("?", "")
            item = item.replace(",", "")
            item = item.replace(".", " ")
            item = item.replace("\"", "")
            item = item.replace("-", " ")
            item = item.replace("!", "")
            item = item.replace("+", "")
            item = item.lower()

            # We only want the line if it doesn't have numbers, and doesn't have a colon, which means its not actual lyrics
            if item not in output_list and lyricsorter.hasNumbers(item) is False and scraper.contains(item, ":") is False:
                output_list.append(lyricsorter.remove_paranthases(item).strip())

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
                            if word != slang_word and slang_word not in word_dict[word]["slang"]:
                                word_dict[word]["slang"].append(slang_word)
    for i, word in enumerate(word_list):
        print("Inserting word #{} of {}".format(str(i), str(len(word_list))))
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

def __reformat_word_table():
    """removes song attribute from all the words"""
    raw_words = list(word_table.scan()['Items'])

    for i, word in enumerate(raw_words):
        print("word #{} of {} total words".format(str(i), str(len(raw_words))))
        Item = {'id': word['id'], 'num_occurrences': word['num_occurrences'], 'slang': word['slang']}
        word_table.put_item(
            Item=Item
        )


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
        try:
            if word_dict[word]['num_occurrences'] > 2:
                pass
            else:
                non_viable_words+=1
                nonviableset.append(word)
        except KeyError:
            non_viable_words += 1
            nonviableset.append(word)


    return(nonviableset)

def create_viable_word_dict():
    viable_words = {"words": []}
    with open("markhov_chains\\master_chain.json") as f:
        data = json.load(f)
    for d in data:
        viable_words["words"].append(d)
    with open('viable_words.json', 'w') as outfile:
        json.dump(viable_words, outfile, indent=2)


def find_viable_words():
    """
    Returns list and dict of words we have found more than one time in song lyrics
    """
    try:
        with open("viable_words.json") as f:
            viableset = json.load(f)["words"]
    except FileNotFoundError:
        response = get_word_list()
        word_list = response[0]
        word_dict = response[1]
        viableset = []
        viable_words = 0

        for word in word_list:
            if word_dict[word]['num_occurrences'] > 2 and word.isalpha():
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
    song_urls = lyricsorter.get_song_url_list()
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
    song_urls = lyricsorter.get_song_url_list()
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



with open('last_word_dict.json') as f:
    last_words = json.load(f)


def __choose_last_word():
    """
    randomly returns a word from list of words we have found at the end of sentences
    """
    global other_time, last_words
    start = time.time()
    try:

        last_words
    except FileNotFoundError:
        response = word_relation_table.get_item(
            Key = {
                'id': "last_words"
            }
        )

        last_words = dict(response['Item']['words'])
        last_words2 = {}
        for item in last_words:
            last_words2[item] = int(last_words[item])
        data = {"data": last_words2}
        #print(data)
        with open('last_word_dict.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)

    words = []
    probabilities = []
    sum = 0
    while True:
        for word in last_words:
            sum += last_words[word]
        for word in last_words:
            words.append(word)
            probabilities.append(float(last_words[word]/sum))
        rand_choice = np.random.choice(words, 1, probabilities)[0]
        if helper_methods.check_phonetic_existance(rand_choice):
            return np.random.choice(words, 1, probabilities)[0]
def __probabilistic_roll(chain: dict):
    """
        Given a dictionary of markov relations and probability, returns a word based on probability of its previous
        occurence
        :param dictionary: of markov relations
        :return: pseudo-random word chosen
        """
    sum = chain["count"]
    words = []
    probabilities = []
    for word in chain["chain"]:
        count = float((chain["chain"][word]["count"]))

        if count ==0:
            count +=1

        probabilities.append(count/sum)
        words.append(word)
    #dprint(probabilities)
    return np.random.choice(words, 1, probabilities)[0]



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

def __get_json_sum(data):
    total = 0
    for item in data:
        total += data[item]
    return total


def count_duplicates(sent):
    """Count the number of duplicate words in a sentence and return that int"""
    d = {word: sent.count(word) for word in sent}
    sum = 0
    for val in d.values():
        sum += (val-1)
    return sum


def construct_sentence(length=5, last_word=None):

    if last_word is None:
        last_word = __choose_last_word()
    if length < 3: length =3
    chunk_size = 3
    i = 0
    sent = []
    while i < length:
        sent.append('')
        i +=1
    i -=1
    sent[i]=last_word

    filename = "markhov_chains" +"\\" +  last_word + '.json'
    #print(filename)
    with open(filename) as f:
        init_chain = json.load(f)
    sent[i-1] = __probabilistic_roll(init_chain)
    curr_chain = init_chain["chain"][sent[i - 1]]
    sent[i-2] = __probabilistic_roll(curr_chain)
    i = i-3

    while i >= 0:
        dprint(last_word)
        dprint(sent)
        # try: #try and do a chain of 4
        #     raise KeyError
        #     with open("markhov_chains" +"\\" +  sent[i+3] + '.json') as f:
        #         curr_chain = json.load(f)
        #         curr_chain = curr_chain["chain"][sent[i+2]]["chain"][sent[i+1]]
        #     dprint(i)
        #     dprint(sent[i+1])
        #     dprint(curr_chain)
        #     sent[i] = __probabilistic_roll(curr_chain)
        #     dprint("FOUR")
        # except (KeyError, ValueError) as e:  #so we settle for a chain of 3
        with open("markhov_chains" +"\\" +  sent[i+2] + '.json') as f:
            curr_chain = json.load(f)
            curr_chain = curr_chain["chain"][sent[i + 1]]
            last_word = sent[i+2]
            dprint(last_word)
            sent[i] = __probabilistic_roll(curr_chain)

            dprint("THREE")
        i -=1

    #print(sent)
    return sent

batch_write = False
if batch_write:
    with open("markhov_chains" + "\\" + "master_chain.json") as f:
        master_chain = json.load(f)


def batch_construct_sentence(length=5, last_word=None):

    global master_chain

    if last_word is None:
        last_word = __choose_last_word()
    if length < 3: length =3
    chunk_size = 3
    i = 0
    sent = []
    while i < length:
        sent.append('')
        i +=1
    i -=1
    sent[i]=last_word

    init_chain = master_chain[last_word]
    sent[i-1] = __probabilistic_roll(init_chain)
    curr_chain = init_chain["chain"][sent[i - 1]]
    sent[i-2] = __probabilistic_roll(curr_chain)
    i = i-3

    while i >= 0:
        dprint(last_word)
        dprint(sent)
        # try: #try and do a chain of 4
        #     raise KeyError
        #     with open("markhov_chains" +"\\" +  sent[i+3] + '.json') as f:
        #         curr_chain = json.load(f)
        #         curr_chain = curr_chain["chain"][sent[i+2]]["chain"][sent[i+1]]
        #     dprint(i)
        #     dprint(sent[i+1])
        #     dprint(curr_chain)
        #     sent[i] = __probabilistic_roll(curr_chain)
        #     dprint("FOUR")
        # except (KeyError, ValueError) as e:  #so we settle for a chain of 3

        curr_chain = master_chain[sent[i+2]]
        curr_chain = curr_chain["chain"][sent[i + 1]]
        last_word = sent[i+2]
        dprint(last_word)
        sent[i] = __probabilistic_roll(curr_chain)

        dprint("THREE")
        i -=1

    #print(sent)
    return sent

def get_first_words():
    pass






def delete_non_viable_words():
    for word in find_nonviable_words():
        print(word)
        word_table.delete_item(
            Key={
                'id': word,
            }
        )
    pass

def get_max_json(a):
    m = 0
    n = 0
    one = " "
    two = " "
    for i, item in enumerate(a):
        if a[item] > m:
            if i > 0:
                n = m
                two = one
            m = a[item]
            one = item
        if a[item] > n and item != one:
            n= a[item]
            two = item

    return [one, two]



def assign_word_specificities():
    """Modifies the data.json file that contains parts of speech tagging such that it chooses the highest 2 frequency
    """
    with open('data.json') as f:
        data = json.load(f)

    gen_types = ["RB","CD", "EX", "DT", "CC", "IN","MD","PDT", "RP", "UH", "TO", "PRP", "WDT", "WP", "WP$","PRP$", "POS", "WRB"]
    for item in data:
        print(item)
        curr_pos = get_max_json(data[item])
        special = True
        for pos in curr_pos:

            if len(pos)>1 and pos in gen_types:
                special = False

        print(special)

        if special:
            helper_methods.update_table(word_table, item, "u", 1)

def write_markov(num=100):
    i=0
    sents = {"sents": []}
    while i<num:
        try:
            sent = construct_sentence(6)
            sents["sents"].append(sent)
            print(sent)
            i+=1
        except ValueError:
            pass
        except KeyError:
            pass
    with open('sample_sentences.json', 'w') as outfile:
        json.dump(sents, outfile, indent=4)

def construct_sentence_pair(length=7, last_word=None):
    first_sent = construct_sentence(length, last_word)
    last_word = first_sent[len(first_sent)-1]
    try:
        rhymes = helper_methods.get_rhymes(last_word)
        print(rhymes)
        last_word = random.choice(rhymes[1])
    except FileNotFoundError:
        print("FNFEEE")
        return None

    sents ={last_word: {smush(first_sent): first_sent}}
    num_elems = 1
    for j in range(13):
        try:
            sent = construct_sentence(length, last_word)
            if smush(sent) not in sents[last_word]:
                sents[last_word][smush(sent)] = sent
                print(sent)
                num_elems+=1
        except (FileNotFoundError, KeyError, IndexError, ValueError) as e:
            pass
        # except (FileNotFoundError):
        #     print("FILENOTFOUND")
        # except( KeyError):
        #     print("KEYERROR")
        # except IndexError:
        #     print("IndexError")

    for i in range(35):

        try:

            if len(rhymes[0])>0:
               # print("first")
                dice = random.randint(0, 1000)

                if (dice%2 == 1):
                    last_word = random.choice(rhymes[0])
                else:
                    last_word = random.choice(rhymes[1])
            else:
                #print("second")
                #print(rhymes[1])
                last_word = random.choice(rhymes[1])
                #print(last_word)
            sent = construct_sentence(length, last_word)

            if last_word not in sents:
                sents[last_word] = {}

            if smush(sent) not in sents[last_word]:
                sents[last_word][smush(sent)] = sent
                num_elems += 1
                print(sent)

        except (FileNotFoundError, KeyError, IndexError, ValueError) as e:
            pass
        # except (FileNotFoundError):
        #     print("FILENOTFOUND")
        # except( KeyError):
        #     print("KEYERROR")
        # except IndexError:
        #     print("IndexError")


    if num_elems > 3:
        return sents

def smush(sent):
    output = ""
    for word in sent:
        output +=word
    return output
#build_sentence(5)
#write_markov(500)
def test_markov(num=7, num2=5):
    for i in range(num):
        print(i)
        # try:
        #     construct_sentence_pair(7)
        # except FileNotFoundError:
        #     pass
        # except KeyError:
        #     pass
        # except ValueError:
        #     pass
        # except IndexError:
        #     pass
        try:
            sents = construct_sentence_pair(num2)
            if sents is not None:
                jprint(sents)
        except ValueError:
            pass

#construct_sentence_pair()

#write_markov()
#test_markov()


def get_all_sents(last_word):
    sents = {}
    k = 0
    for i in range(1000):
        length = random.randint(4,6)

        try:
            sent = batch_construct_sentence(length, last_word)
            if smush(sent) not in sents:
                sents[smush(sent)] = sent
                k=k+1


        except (FileNotFoundError, KeyError, IndexError, ValueError) as e:
            pass
    return sents


def populate_sentence_db():
    with open('last_word_dict.json') as f:
        last_words = dict(json.load(f))
    sent_list = []
    i = 1
    while i < len(list(last_words.keys())):
        try:
            word = list(last_words.keys())[i]
            print(word)
            print(i)

            if helper_methods.check_phonetic_existance(word):
                sents = get_all_sents(word)
                response = lyric_table.get_item(
                    Key={
                        'id': -1
                    }
                )

                total = int(response['Item']['total'])
                start = total+1

                with lyric_table.batch_writer() as batch:
                    for j, sent in enumerate(sents):

                        total+=1

                        Item = {'id': total, 'sent': sents[sent], 'len': len(sents[sent])}
                        for w in sents[sent]:
                            Item[w] = 1
                        batch.put_item(
                            Item=Item
                        )
                        sent_list.append(sents[sent])
                    batch.put_item(Item={'id': -1, 'total': total})
                    helper_methods.update_table(rhyme_table,word,"sent_ids", [start, total])
            else:
                print("{} has no phonetic representation".format(word))

            i += 1
        except botocore.exceptions.ClientError:
            i += 1
    output_sents = {"sents": sent_list}
    with open('sent_array.json', 'w') as outfile:
        json.dump(sent_list, outfile, indent=2)

def create_word_db_links():
    with open('sent_array.json') as f:
        sents = dict(json.load(f))
    output = {}
    sents = sents["sents"]
    for i, sent in enumerate(sents):
        print(i)
        index = i+2
        words = list(set(sent))
        for word in words:
            if word not in output:
                output[word] = {"count": 0, "ids": []}
            output[word]["count"] +=1
            output[word]["ids"].append(index)

    with open('word_db_map.json', 'w') as outfile:
        json.dump(output, outfile, indent=2)

def update_word_db_links():
    with open('word_db_map.json') as f:
        data = dict(json.load(f))
    for i, word in enumerate(data):
        print(i)
        if data[word]["count"] > 1000:
            while data[word]["count"] % 1000 != 0:
                data[word]["ids"].append(random.choice(data[word]["ids"]))
                data[word]["count"] +=1


    with open('word_db_map_2.json', 'w') as outfile:
        json.dump(data, outfile, indent=2)

def insert_word_db_mappings():
    with open('word_db_map_2.json') as f:
        data = dict(json.load(f))
    with lyric_link_table.batch_writer() as batch:
        for i, word in enumerate(data):
            print(i)
            num_entries = int(max(int(data[word]["count"]/1000), 1))
            batch.put_item(Item={'id': word, 'count': num_entries})
            for j in range(num_entries):
                batch.put_item(Item={'id': word+"-"+str(j+1), 'links': data[word]["ids"][j*1000:(j+1)*1000]})




insert_word_db_mappings()
