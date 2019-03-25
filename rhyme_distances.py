# -*- coding: utf-8 -*-
"""
Created on Sat Aug 25 13:26:26 2018
This file contains methods to calculate the rhyme distance between two given
words. It will be used to determine how well two words rhyme
@author: Adm
"""

from helper_methods import jprint
import math
import word_processor as wp

import helper_methods as helper


import boto3
import metaphone as met

import json

dynamodb = boto3.resource("dynamodb")
word_relation_table = dynamodb.Table("WordRelation")
with open("rhymes\\master_rhymes.json") as f:
    confirmed_rhymes = json.load(f)

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



def memoize(func):
    """This method optimizes the runtime of edit_distance method by storing
    some of the values needed in the recursive calls"""

    mem = {}

    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in mem:
            mem[key] = func(*args, **kwargs)
        return mem[key]

    return memoizer


@memoize
def edit_dist(a, b):
    """This method implements the usual edit_distance algorithm."""
    if a == "":
        return len(b)
    if b == "":
        return len(a)
    if a[-1] == b[-1] and (a[-1] in ("a", "e", "i", "o", "u") and b[-1] in ("a", "e", "i", "o", "u")):
        cost = -1
    elif a[-1] == b[-1]:
        cost = 0
    else:
        cost = 1

    res = min([edit_dist(a[:-1], b) + 1,
               edit_dist(a, b[:-1]) + 1,
               edit_dist(a[:-1], b[:-1]) + cost])

    return res


def metaphone_dist(met1: str, met2: str, alliteration=False):
    if len(met1) < len(met2):
        small = met1
        large = met2
    else:
        small = met2
        large = met1

    if alliteration:
        # Ensures that focus is given to first letters
        if len(small) > 3:
            split = max(math.floor(len(small) / 2), 3) + 1
            return edit_dist(large[:split], small[:split]) * split + edit_dist(large[split:], small[split:])
        else:
            return edit_dist(large[:len(large) - len(small) + 2], small) * 3

    else:
        # Ensures that focus is given to last letters
        if len(small) > 3:
            split = max(math.floor(len(small) / 2), 3)
            return edit_dist(large[split:], small[split:]) * split + edit_dist(large[:split], small[:split])
        else:
            return edit_dist(large[len(large) - len(small):], small) * 3


def rhyme_dist(p1, p2, tune=[4, 1], dist=0):
    """This function return the phonetic distance between two words, while
    prioraizing rhymes (i.e. rhymes that occur in the end of
    word).The tunning parameter is a list, where the first entry corresponds to
    the syllable size to be compared and the second corresponds to weight
    adjustments.
    """

    size = tune[0]
    weight = tune[1]

    if weight == 1 and len(p1) < size:
        dist = edit_dist(p1, p2[len(p2) - len(p1):])

    elif weight == 1 and len(p2) < size:
        dist = edit_dist(p1[len(p1) - len(p2):], p2)

    elif len(p1) >= size and len(p2) >= size:
        dist += edit_dist(p1[len(p1) - size:], p2[len(p2) - size:]) / weight

    else:
        return dist

    return rhyme_dist(p1[:-size], p2[:-size], [size, weight + 1], dist)


def alliteration_dist(p1, p2, tune=[4, 1], dist=0):
    """This function returns the phonetic distance between two words, while
    prioritizing alliteration rhyme (i.e. rhymes that occur in the beginning of
    word).The tune parameter is a list, where the first entry corresponds to
    the syllable size to be compared and the second corresponds to weight
    adjustments.
    """

    size = tune[0]
    weight = tune[1]

    # do we need the +1 here?
    if weight == 1 and len(p1) < size:
        dist = edit_dist(p1, p2[:len(p1) + 1])

    elif weight == 1 and len(p2) < size:
        dist = edit_dist(p1[:len(p2) + 1], p2)

    elif len(p1) >= size and len(p2) >= size:
        dist += edit_dist(p1[:size + 1], p2[:size + 1]) / weight

    else:
        return dist

    return alliteration_dist(p1[size + 1:], p2[size + 1:], [size, weight + 1], dist)


def phonetic_dist(p1, p2, alliteration=False, tune=[4, 1], ):
    """This method gives the rhyme distance between two given words, based on
    edit distance"""

    # formats input to distance functions
    p1 = helper.phonetic_clean(str(p1))
    p2 = helper.phonetic_clean(str(p2))
    p1 = str(p1).replace("\'", "")
    p2 = str(p2).replace("\'", "")

    # if alliteration is set to True, compare initial overlapping syllables
    if alliteration:
        return alliteration_dist(p1, p2, tune)

    # if alliteration is set to False, compare last overlapping syllables
    else:
        return rhyme_dist(p1, p2, tune)


def met_dist(word_1: str, word_2: str):
    return metaphone_dist(met.doublemetaphone(word_1)[0], met.doublemetaphone(word_2)[0])


def dist(word_1: str, word_2: str, alliteration=False):
    # get phonetic and metaphone of word to be compared

    try:
        info_1 = all_phonetics[word_1]
        info_2 = all_phonetics[word_2]
        info_1 = clean_phonetics(info_1)
        info_2 = clean_phonetics(info_2)
    except KeyError:
        #print(word_1)
        #print(word_2)
        #print("Word not in database")
        return 1

    phon_dist = phonetic_dist(info_1[0], info_2[0], alliteration)
    meta_dist = metaphone_dist(info_1[1], info_2[1], alliteration)
    total_dist = adjust_range(phon_dist, meta_dist)

    return total_dist




def metaphone_rhyme(word: str, all_phonetics, thresh=10, alliteration=False):
    """This function returns a list of the closest phonetic matches from a given word based on Metaphone encoding and a
    variation of minimum edit distance function"""

    # get phonetic and metaphone of word to be compared
    info = helper.get_by_id(word, word_relation_table)
    word_info = [info['id'], info['phonetic'], met.doublemetaphone(info['id'])[0]]
    print(word_info[2])
    matches = []

    # Compare distance between input word and all other viable words
    for i in range(len(all_phonetics)):

        current_word = all_phonetics[i]

        # only compares words that differ
        if word_info[0] != current_word[0]:

            metaphone_dist = metaphone_dist(word_info[2], current_word[2], alliteration)

            # while matches is not full, populate list
            if len(matches) < thresh:
                matches.append({"word": current_word[0], "d": metaphone_dist, "Met": current_word[2]})
            else:
                if matches[thresh - 1]["d"] > metaphone_dist:
                    matches[thresh - 1] = {"word": current_word[0], "d": metaphone_dist, "Met": current_word[2]}

        matches = sorted(matches, key=lambda k: k['d'])

    return matches


def phonetic_rhyme(word: str, all_phonetics, thresh=10, alliteration=False):
    """This function returns a list of the closest phonetic matches from a given word based on the "phonetic_dist function"""

    # get phonetic and metaphone of word to be compared
    info = helper.get_by_id(word, word_relation_table)
    word_info = [info['id'], info['phonetic'], met.doublemetaphone(info['id'])[0]]
    print(word_info[1])
    matches = []

    # Compare distance between input word and all other viable words
    for i in range(len(all_phonetics)):

        current_word = all_phonetics[i]

        # only compares words that differ and long enough words
        if word_info[0] != current_word[0] and len(current_word[0]) > 3:

            phon_dist = phonetic_dist(word_info[1], current_word[1], alliteration)

            # while matches is not full, populate list
            if len(matches) < thresh:
                matches.append({"word": current_word[0], "d": phon_dist, "Phon": current_word[1]})
            else:
                if matches[thresh - 1]["d"] > phon_dist:
                    matches[thresh - 1] = {"word": current_word[0], "d": phon_dist, "Phon": current_word[1]}

        matches = sorted(matches, key=lambda k: k['d'])

    return matches


def adjust_range(d1, d2):
    # Since we are not interested in rhymes that are too weak, we limit our analysis to the cases that yield
    # distances smaller than 10. i.e. focus on range -3,10 for safe margin. This function returns a value between 0 and 1
    # d1 is phon_dist and d2 is meta_dist

    total_dist = d1 + d2 * 0.5

    if total_dist >= 10:
        return 1

    elif total_dist <= -3:
        return 0

    else:
        return (total_dist + 3) / 13


def rhyme_list(word: str, thresh=30, alliteration=False):
    # get phonetic and metaphone of word to be compared

    try:
        info = all_phonetics[word]
        info = clean_phonetics(info)
        #jprint(info)
    except KeyError:
        print("Word not in database")
        return None

    matches = []

    # Compare distance between input word and all other viable words
    id = list(all_phonetics.keys())
    for i in range(len(all_phonetics)):

        current_word = id[i]
        current_info = all_phonetics[current_word]
        current_info = clean_phonetics(current_info)
        # only compares words that differ and long enough words
        if word != current_word and len(current_word) > 3:

            phon_dist = phonetic_dist(info[0], current_info[0], alliteration)
            meta_dist = metaphone_dist(info[1], current_info[1], alliteration)
            total_dist = adjust_range(phon_dist, meta_dist)

            # while matches is not full, populate list
            if len(matches) < thresh:
                matches.append({"word": current_word, "d": total_dist, "Phon": current_info[0]})
            else:
                if matches[thresh - 1]["d"] > phon_dist:
                    matches[thresh - 1] = {"word": current_word, "d": total_dist, "Phon": current_info[0]}

        matches = sorted(matches, key=lambda k: k['d'])

    return matches

def clean_phonetics(info):
    consonants = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'y', 'z']
    found_vowel = False
    first_syllable = ""
    other = ['[', '\'', '\"']
    sound = info[0]
    #print(sound)
    sound = sound
    for letter in sound:
        if letter not in consonants and letter not in other:
            found_vowel = True
        if found_vowel and letter not in other:
            first_syllable += letter
        if letter in other:
            first_syllable += letter
    #print(first_syllable)
    info[0] = first_syllable

    return info

def populate_rhymes():
    viable_words = wp.find_viable_words()
    master_rhymes = {}
    i = 10000
    while i < 14000:
        print(i)
        word = viable_words[i]
        master_rhymes[word] = {}
        data = rhyme_list(word)
        if data is not None:
            for d in data:
                w = d["word"]
                distance = d["d"]
                if distance <= 0.30:
                    master_rhymes[word][w] = distance
            with open('rhymes\\' + word +  '.json', 'w') as outfile:
                json.dump(master_rhymes[word], outfile, indent=4)
        i+=1

#jprint(rhyme_list("trio"))
#populate_rhymes()

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


#get_rhymes("ass")
