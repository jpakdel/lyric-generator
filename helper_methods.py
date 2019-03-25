# -*- coding: utf-8 -*-
"""
Created on Sat Aug 25 17:58:02 2018
This file contains auxiliary methods to be further organized into more
specific folders
@author: Adm
"""
import json
import boto3
import random
#import scrapping_methods as sm
#import word_processor as wp

dynamodb = boto3.resource("dynamodb")
proxy_table = dynamodb.Table("Proxy")
word_table = dynamodb.Table("Word")
song_table = dynamodb.Table("Song")
word_relation_table = dynamodb.Table("WordRelation")
debug = False

with open("rhymes\\master_rhymes.json") as f:
    confirmed_rhymes = json.load(f)
def jprint(dic):
    print(json.dumps(dic, indent=2))

def get_song_url_list():
    """
    returns list of all the song urls in our database, which are the unique identifiers we use to track their lyrics
    :return:
    """
    response = song_table.get_item(
        Key={
            'id': "mapmap"
        }
    )
    maps = list(response['Item']['map_list'])
    song_url_list = []
    for map in maps:
        response = song_table.get_item(
            Key={
                'id': map
            }
        )
        song_url_list.extend(list(response['Item']['url_list']))

    return (song_url_list)

def get_all_sentence_array():
    #I have this option set to true because I already saved it in JSON
    option_json = True
    if option_json:
        with open('rap_sentences_array.json', 'r') as f:
            corpus = json.load(f)
            return corpus['value']
    song_urls = get_song_url_list()
    sentences = []

    #This is the part of the code that executed once and saved it as a variable
    for i, link in enumerate(song_urls):
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
            if len(line)>2 and len(line)<13:
                sentences.append(line)
        #new song marker
        sentences.append([['']])
        print(i)
        print("")

    sent_array = {
        "value": sentences
    }
    with open('rap_sentences_array.json', 'w') as outfile:
        json.dump(sent_array, outfile, indent=4)
    pass
    return sentences

def word_relation_lookup(label):
    #print(label)
    file_path = "word_relation/" + label +".json"
    try:

        with open(file_path) as f:
            data = json.load(f)
            data = data["data"]
            #print("file found")
    except FileNotFoundError:
        #print("file not found")
        response = word_relation_table.get_item(
            Key={
                'id': label
            }
        )
        data = response['Item']['words']
        out_data = {}
        for item in data:
            out_data[item] = int(data[item])

        out_data = {"data": out_data}
        with open(file_path, 'w') as outfile:
            json.dump(out_data, outfile, indent=4)

    return data


def get_proxy():
    """
    Looks up a random proxy from DynamoDB table and returns it
    :returns array of two strings, IP and port:
    """
    response = proxy_table.get_item(
        Key={
            'id': "num_proxies"
        }
    )
    item = response['Item']
    num_proxies = int(item['value'])
    choice = random.randint(0, num_proxies - 1)
    response = proxy_table.get_item(
        Key={
            'id': str(choice)
        }
    )
    item = response['Item']
    proxy_response = [item["ip"], item["port"]]
    return proxy_response


def update_table(table, id: str, key: str, value: str):
    """Updates user table, just for saving space.
    Args: table is the table we are updating, id is the id of the item we are updating, key is the attribute name, and
    value is the attribute value.
    """
    table.update_item(
        Key={
            'id': id,
        },
        UpdateExpression='SET ' + key + ' = :val1',
        ExpressionAttributeValues={
            ':val1': value
        }
    )
    return


def get_word(table):
    """
    Looks up a random proxy from DynamoDB table and returns it
    :returns array of two strings, IP and port:
    """

    return list(table.scan()['Items'])


def get_by_id(entry_id, table):
    """This function returns the correspondent entry of an input id in the
    refered table. It is used in get_rhyme_list for example, in order to get
    the phonetic of a single word and then compare it to others."""

    response = table.get_item(
        Key={
            'id': entry_id
        }
    )

    return response['Item']

def phonetic_clean(word: str):
    """
    This function formats the output phonetic by erasing the characters:
    , "]", ",", "-", " ", ";" from the output
    """

    initial_length = len(word)
    modified_word = word
    counter = 0

    while (counter < initial_length):
        current = modified_word[counter:counter + 1]
        if (current == "[" or current == "]" or current == " " or
                current == "," or current == "-" or current == ";"):
            modified_word = modified_word[:counter] + modified_word[counter + 1:]
            counter -= 1

        counter += 1
    return modified_word


def __update_next_stop(raw_phonetic, next_stop, i):
    """This function is a minor helper function to deal with some exceptions
    in the html scrapping. It corrects cases in which the phonetic of a word
    has sylables separated by "," and "-" """

    next_stop_updated = next_stop
    next_1 = raw_phonetic[i + 2:next_stop - 1].find("-")
    next_2 = raw_phonetic[i + 1:next_stop - 1].find(",")

    next_syllable = min(next_1, next_2)

    if next_1 == -1:
        next_syllable = next_2
    if next_2 == -1:
        next_syllable = next_1

    if (next_syllable != -1 and raw_phonetic[next_syllable + 3 + i] != "<"):
        raw_phonetic = raw_phonetic[:next_syllable + i + 2] + ">" + raw_phonetic[next_syllable + i + 2:]
        next_stop_updated = next_syllable + i + 2

    return [raw_phonetic, next_stop_updated]


def __phonetic_scrape_helper(word: str, word_scraped: str):
    start_index = (word.find(word_scraped), word_scraped.find(word))
    append_where = 0
    # tells caller where extra_letters must be appended (1 end or 2 start)

    l1 = len(word_scraped)

    if start_index[0] != -1:
        if start_index[0] == 0:
            extra_letters = word[l1:]
            append_where = 1
        else:
            extra_letters = word[:start_index[0]] + "-" + word[start_index[0] + l1:]
            append_where = 2
        return (extra_letters, append_where)

    if start_index[1] != -1:
        if start_index[1] == 0:
            extra_letters = word_scraped[l1:]
            append_where = 1
        else:
            extra_letters = word_scraped[:start_index[1]] + "-" + word_scraped[start_index[1] + l1:]
            append_where = 2
        return (extra_letters, append_where)

    if start_index == (-1, -1):
        return (-1, append_where)


def get_phonetic():
    """This methods outputs a dictionary with all words and phonetic representation
    in the database. It will be used to increase the speed in which we find the
    rhymes/alliteration of a given word"""

    words = get_word(word_table)
    output = []

    # exclude items with a count number attached
    # TODO: change range of for loop to extend from 1 to range(len(words)).
    # Set to 100 for fast testing.
    for i in range(100):
        get_id = words[i]["id"]
        response = word_relation_table.get_item(
            Key={
                "id": get_id
            }
        )
        if "Item" in response:
            print(i)
            output.append(response["Item"])

    return output

def find_viable_words():
    """
    Returns list and dict of words we have found more than one time in song lyrics
    """
    with open("viable_words.json") as f:
        viableset = json.load(f)["words"]

    return(viableset)

def get_all_phonetic_array():
    # I have this option set to true because I already saved it in JSON
    option_json = True
    if option_json:
        with open('rap_phonetic_array.json', 'r') as f:
            corpus = json.load(f)
            return corpus

all_phonetics = get_all_phonetic_array()

def check_phonetic_existance(word):
    """ Checks to see if we have a phonetic representation for word"""
    if word not in all_phonetics:
        return False
    return True

def dprint(word):
    global debug
    if debug:
        print(word)

def update_phonetics():
    """This method goes over all entries of word_relation table and checks if each word entry
     (not containing "_") has a phonetic. If not, it updates the phonetic."""

    entries = wp.find_viable_words()
    count = 0

    for i in range(len(entries)):

        print(i)

        # Gets the correspondent element in word_relation table
        try:
            word_relation_entry = get_by_id(entries[i], word_relation_table)

            if 'phonetic' not in word_relation_entry:
                new_phon, word = sm.phonetic_scrape(entries[i])

                if new_phon is not -1:
                    update_table(word_relation_table, entries[i], 'phonetic', '[' + ','.join(new_phon) + ']')
                    count = count + 1

        except KeyError:
            new_phon, word = sm.phonetic_scrape(entries[i])
            if new_phon is not -1:

                count = count + 1
                word_relation_table.put_item(
                    Item={
                        'id': entries[i],
                        'phonetic': '[' + ','.join(new_phon) + ']',
                    }
                )

    return count

def get_rhymes(word):
    global confirmed_rhymes
    rhymes = confirmed_rhymes[word].keys()
    output = [[],[]]
    for item in rhymes:
        output[0].append(item)
    with open ("rhymes\\" + word + ".json") as f:
        data = json.load(f)

    for item in data:
        output[1].append(item)
    return output
