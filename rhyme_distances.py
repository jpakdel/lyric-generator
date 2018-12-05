# -*- coding: utf-8 -*-
"""
Created on Sat Aug 25 13:26:26 2018
This file contains methods to calculate the rhyme distance between two given
words. It will be used to determine how well two words rhyme
@author: Adm
"""

import helper_methods as helper
import math
import word_processor as wp
import scraper
import helper_methods as helper
import rhyme_distances as rdist
import scrapping_methods as sm
import boto3
import metaphone as met
import lyricsorter as lsorter
import json



word_relation_table = dynamodb.Table("WordRelation")


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
    if a[-1] == b[-1] and (a[-1] in ("a","e", "i", "o", "u") and b[-1] in ("a","e", "i", "o", "u")):
        cost = -1
    elif a[-1] == b[-1]:
        cost = 0
    else:
        cost = 1

    res = min([edit_dist(a[:-1], b) + 1,
               edit_dist(a, b[:-1]) + 1,
               edit_dist(a[:-1], b[:-1]) + cost])

    return res

def metaphone_dist(met1:str, met2:str, alliteration=False):

    if len(met1)<len(met2):
        small = met1
        large = met2
    else:
        small = met2
        large = met1

    if alliteration:
        #Ensures that focus is given to first letters
        if len(small) > 3:
            split = max(math.floor(len(small) / 2),3)+1
            return edit_dist(large[:split], small[:split])*split + edit_dist(large[split:], small[split:])
        else:
            return edit_dist(large[:len(large)-len(small)+2], small) * 3

    else:
        #Ensures that focus is given to last letters
        if len(small) > 3:
            split = max(math.floor(len(small) / 2),3)
            return edit_dist(large[split:], small[split:])*split + edit_dist(large[:split], small[:split])
        else:
            return edit_dist(large[len(large)-len(small):], small) * 3



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
        dist = edit_dist(p1, p2[:len(p1)+1])

    elif weight == 1 and len(p2) < size:
        dist = edit_dist(p1[:len(p2)+1], p2)

    elif len(p1) >= size and len(p2) >= size:
        dist += edit_dist(p1[:size+1], p2[:size+1]) / weight

    else:
        return dist

    return alliteration_dist(p1[size+1:], p2[size+1:], [size, weight + 1], dist)


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



def met_dist(word_1:str, word_2:str):

    return rdist.metaphone_dist(met.doublemetaphone(word_1)[0], met.doublemetaphone(word_2)[0])

def metaphone_rhyme(word:str, all_phonetics, thresh = 10, alliteration = False):
    """This function returns a list of the closest phonetic matches from a given word based on Metaphone encoding and a
    variation of minimum edit distance function"""

    #get phonetic and metaphone of word to be compared
    info = helper.get_by_id(word, word_relation_table)
    word_info = [info['id'], info['phonetic'], met.doublemetaphone(info['id'])[0]]
    print(word_info[2])
    matches = []

    # Compare distance between input word and all other viable words
    for i in range(len(all_phonetics)):

        current_word = all_phonetics[i]

        #only compares words that differ
        if word_info[0] != current_word[0]:

            metaphone_dist = metaphone_dist(word_info[2], current_word[2], alliteration)

            # while matches is not full, populate list
            if len(matches) < thresh:
                matches.append({"word": current_word[0], "d": metaphone_dist, "Met": current_word[2]})
            else:
                if matches[thresh-1]["d"] > metaphone_dist:
                    matches[thresh-1] = {"word": current_word[0], "d": metaphone_dist, "Met": current_word[2]}


        matches = sorted(matches, key=lambda k: k['d'])

    return matches

def phonetic_rhyme(word:str, all_phonetics, thresh = 10, alliteration = False):
    """This function returns a list of the closest phonetic matches from a given word based on the "phonetic_dist function"""

    #get phonetic and metaphone of word to be compared
    info = helper.get_by_id(word, word_relation_table)
    word_info = [info['id'], info['phonetic'], met.doublemetaphone(info['id'])[0]]
    print(word_info[1])
    matches = []

    # Compare distance between input word and all other viable words
    for i in range(len(all_phonetics)):

        current_word = all_phonetics[i]

        #only compares words that differ and long enough words
        if word_info[0] != current_word[0] and len(current_word[0]) > 3:

            phon_dist = phonetic_dist(word_info[1], current_word[1], alliteration)

            # while matches is not full, populate list
            if len(matches) < thresh:
                matches.append({"word": current_word[0], "d": phon_dist, "Phon": current_word[1]})
            else:
                if matches[thresh-1]["d"] > phon_dist:
                    matches[thresh-1] = {"word": current_word[0], "d": phon_dist, "Phon": current_word[1]}


        matches = sorted(matches, key=lambda k: k['d'])

    return matches

def rhyme_list(word:str, thresh = 10, alliteration = False):

    #get phonetic and metaphone of word to be compared
    all_phonetics = get_all_phonetic_array()
    try:
        info = helper.get_by_id(word, word_relation_table)
    except KeyError:
        print("Word not in database")
        return


    word_info = [info['id'], info['phonetic'], met.doublemetaphone(info['id'])[0]]
    print(word_info[1])
    matches = []

    # Compare distance between input word and all other viable words
    for i in range(len(all_phonetics)):

        current_word = all_phonetics[i]

        #only compares words that differ and long enough words
        if word_info[0] != current_word[0] and len(current_word[0]) > 3:

            phon_dist = phonetic_dist(word_info[1], current_word[1], alliteration)
            meta_dist = metaphone_dist(word_info[2], current_word[2], alliteration)

            # while matches is not full, populate list
            if len(matches) < thresh:
                matches.append({"word": current_word[0], "d": phon_dist + meta_dist*0.5, "Phon": current_word[1]})
            else:
                if matches[thresh-1]["d"] > phon_dist:
                    matches[thresh-1] = {"word": current_word[0], "d": phon_dist + meta_dist*0.5, "Phon": current_word[1]}


        matches = sorted(matches, key=lambda k: k['d'])

    return matches


def get_all_phonetic_array():
    # I have this option set to true because I already saved it in JSON
    option_json = True
    if option_json:
        with open('rap_phonetic_array.json', 'r') as f:
            corpus = json.load(f)
            return corpus['phonetics']
    viable_words = wp.find_viable_words()
    print(len(viable_words))
    dic = []

    # This is the part of the code that executed once and saved it as a variable

    for i in range(len(viable_words)):
        print(i)

        try:
            entry = helper.get_by_id(viable_words[i], word_relation_table)
            dic.append((entry['id'], entry['phonetic'], met.doublemetaphone(entry['id'])[0]))

        except KeyError:
            print('item not found')

    phonetic_array = {
        "phonetics": dic
    }
    with open('rap_phonetic_array.json', 'w') as outfile:
        json.dump(phonetic_array, outfile, indent = 4)
    pass
    return dic

# This is the old version of method
"""
def rhyme_degree(phonetic_1, phonetic_2):

    #only compare the last syllables of both words
    size_1 = len(phonetic_1)
    size_2 = len(phonetic_2)
    num_to_compare = min(size_1, size_2)

    extra_syllables = max(size_1-num_to_compare, size_2-num_to_compare)

    # the more different the size is between the words, increase the total cost
    total = 0
    if extra_syllables == 1:
        total = 0.5
    if extra_syllables == 2:
        total = 1
    if extra_syllables >= 3:
        total = 3

    # last syllable is weighted twice as much
    weight_syllable = 1
    distances = []

    for i in range(1, num_to_compare + 1):

        # measure distance of last syllable
        if i == 1:  

            total_dist = edit_dist(phonetic_1[size_1-i],phonetic_2[size_2-i])
            syllable_size = min(len(phonetic_1[size_1-i]),len(phonetic_2[size_2-i]))

            # need to assign smaller weight than 2 if we can find substring:
            # (i.e kahyt and bahy)
            # find smaller word
            appended = False
            if syllable_size == len(phonetic_1[size_1-i]):
                if (phonetic_1[size_1-i].find(phonetic_2[size_2-i][:-1]) != -1):
                    distances.append(total_dist)
                    appended = True
                if (phonetic_1[size_1-i].find(phonetic_2[size_2-i][1:]) != -1):
                    distances.append(total_dist * 0.5)
                    appended = True

            if syllable_size == len(phonetic_2[size_2-i]):
                if (phonetic_2[size_2-i].find(phonetic_1[size_1-i][:-1]) != -1):
                    distances.append(total_dist)
                    appended = True      
                if (phonetic_2[size_2-i].find(phonetic_1[size_1-i][1:]) != -1):
                    distances.append(total_dist*0.5)
                    appended = True

            # if only first letter of syllable differs
            if (total_dist == 1 and edit_dist(phonetic_1[size_1-i][1:], 
                              phonetic_2[size_2-i][1:]) == 0 and ~appended):
                distances.append(total_dist * 0.5)

            # if first two letters of syllable differs
            if (total_dist == 2 and edit_dist(phonetic_1[size_1-i][2:], 
                              phonetic_2[size_2-i][2:]) == 0 and ~appended):
                distances.append(total_dist * 0.5)                    
            else:  
                distances.append(total_dist*2*weight_syllable)

        else:
            distances.append(edit_dist(phonetic_1[size_1-i],phonetic_2[size_2-i])*weight_syllable)

        total += distances[i - 1]
    return total
"""
