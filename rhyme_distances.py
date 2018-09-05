# -*- coding: utf-8 -*-
"""
Created on Sat Aug 25 13:26:26 2018

This file contains methods to calculate the rhyme distance between two given 
words. It will be used to determine how well two words rhyme

@author: Adm
"""

def memoize(func):
    mem = {}
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in mem:
            mem[key] = func(*args, **kwargs)
        return mem[key]
    return memoizer


# Within sylable, distance assigns greater weight to initial letters
# Within whole phonetic, distance assigns greater weight to initial sylables   
# apple aple
@memoize    
def edit_distance(a, b):
    if a == "":
        return len(b)
    if b == "":
        return len(a)
    if a[-1] == b[-1]:
        cost = 0
    else:   
        cost = 2

    res = min([edit_distance(a[:-1], b)+1,
               edit_distance(a, b[:-1])+1, 
               edit_distance(a[:-1], b[:-1]) + cost])
    return res  
  
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
    #weight_syllable = 0.5/(num_to_compare-1)
    weight_syllable = 1
    distances = []
    
    for i in range(1, num_to_compare + 1):
        
        # measure distance of last syllable
        if i == 1:  
            
            total_dist = edit_distance(phonetic_1[size_1-i],phonetic_2[size_2-i])
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
            if (total_dist == 1 and edit_distance(phonetic_1[size_1-i][1:], 
                              phonetic_2[size_2-i][1:]) == 0 and ~appended):
                distances.append(total_dist * 0.5)
                
            # if first two letters of syllable differs
            if (total_dist == 2 and edit_distance(phonetic_1[size_1-i][2:], 
                              phonetic_2[size_2-i][2:]) == 0 and ~appended):
                distances.append(total_dist * 0.5)                    

            else:  
                distances.append(total_dist*2*weight_syllable)
                
        else:
            distances.append(edit_distance(phonetic_1[size_1-i],phonetic_2[size_2-i])*weight_syllable)
        
        total += distances[i - 1]

    return total
