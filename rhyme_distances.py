# -*- coding: utf-8 -*-
"""
Created on Sat Aug 25 13:26:26 2018

This file contains methods to calculate the rhyme distance between two given 
words. It will be used to determine how well two words rhyme

@author: Adm
"""

import helper_methods as helper

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
    if a[-1] == b[-1]:
        cost = 0
    else:
        cost = 1

    res = min([edit_dist(a[:-1], b)+1,
               edit_dist(a, b[:-1])+1, 
               edit_dist(a[:-1], b[:-1]) + cost])
        
    return res      

def rhyme_dist(p1, p2, tune = [3,1], dist = 0):
    
    """This function return the phonetic distance between two words, while 
    prioraizing rhymes (i.e. rhymes that occur in the end of
    word).The tunning parameter is a list, where the first entry corresponds to 
    the syllable size to be compared and the second corresponds to weight 
    adjustments.
    """
    
    size = tune[0]
    weight = tune[1]
    
    if weight == 1 and len(p1) < 3:
        dist = edit_dist(p1, p2[len(p2)-len(p1):])
        
    elif weight == 1 and len(p2) < 3:
        dist = edit_dist(p1[len(p1)-len(p2):], p2)

    elif len(p1) >= 3 and len(p2) >= 3:
        dist += edit_dist(p1[len(p1)-size:],p2[len(p2)-size:])/weight
    
    else:
        return dist
    
    
    return rhyme_dist(p1[:-size],p2[:-size], [size, weight + 1], dist)
    

def alliteration_dist(p1, p2, tune = [3,1], dist = 0):
    
    """This function returns the phonetic distance between two words, while 
    prioraizing alliteration rhyme (i.e. rhymes that occur in the beggining of
    word).The tune parameter is a list, where the first entry corresponds to 
    the syllable size to be compared and the second corresponds to weight 
    adjustments.
    """
        
    size = tune[0]
    weight = tune[1]
    
    if weight == 1 and len(p1) < 3:
        dist = edit_dist(p1, p2[:len(p1)])
        
    elif weight == 1 and len(p2) < 3:
        dist = edit_dist(p1[:len(p2)], p2)

    elif len(p1) >= 3 and len(p2) >= 3:
        dist += edit_dist(p1[:size],p2[:size])/weight
    
    else:
        return dist
    
    
    return rhyme_dist(p1[size:],p2[size:], [size, weight + 1], dist)
        
   
def phonetic_dist(p1, p2, tune = [3,1], alliteration = False):
    """This method gives the rhyme distance between two given words, based on 
    edit distance priciples"""
    
    # formats input to distance functions
    p1 = helper.phonetic_clean(str(p1))
    p2 = helper.phonetic_clean(str(p2))
    p1 = str(p1).replace("\'", "")
    p2 = str(p2).replace("\'", "")
       
    #if alliteration is set to True, compare initial overlapping syllables
    if alliteration:
        return alliteration_dist(p1,p2, tune)
    
    #if alliteration is set to False, compare last overlapping syllables
    else:
        return rhyme_dist(p1, p2, tune)
       
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
