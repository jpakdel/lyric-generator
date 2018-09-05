# -*- coding: utf-8 -*-
"""
Created on Sat Aug 25 17:58:02 2018

This file contains auxiliary methods to be further organized into more 
specific folders
@author: Adm
"""

import boto3
import random

dynamodb = boto3.resource("dynamodb", region_name='us-east-1')

proxy_table = dynamodb.Table("Proxy")
word_table = dynamodb.Table("Word")
song_table = dynamodb.Table("Song")


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
    choice = random.randint(0, num_proxies-1)
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

def get_word():
    """
    Looks up a random proxy from DynamoDB table and returns it
    :returns array of two strings, IP and port:
    """
    
    return list(word_table.scan()['Items'])   

def phonetic_clean(word:str):
    
    """
    This function formats the output phonetic by erasing the characters:
    , "]", ",", "-", " ", ";" from the output 
    """
    
    initial_length = len(word)
    modified_word = word
    counter = 0
                        
    while(counter < initial_length):
        current = modified_word[counter:counter+1]
        if (current == "[" or current == "]" or current == " " or 
            current == "," or current == "-" or current == ";"):
            modified_word = modified_word[:counter] + modified_word[counter+1:]
            counter -= 1
        
        counter += 1
    return modified_word
  
def update_next_stop(raw_phonetic, next_stop, i):
    
    next_stop_updated = next_stop
    next_1 = raw_phonetic[i+2:next_stop-1].find("-")
    next_2 = raw_phonetic[i+1:next_stop-1].find(",")
                
    next_syllable = min(next_1, next_2)
                
    if next_1 == -1:
        next_syllable = next_2
    if next_2 == -1:
        next_syllable = next_1
                
    if (next_syllable != -1 and raw_phonetic[next_syllable + 3 + i] != "<"):
        raw_phonetic = raw_phonetic[:next_syllable + i + 2] + ">" + raw_phonetic[next_syllable + i + 2:]
        next_stop_updated = next_syllable + i + 2
        
    return [raw_phonetic, next_stop_updated]

def phonetic_scrape_helper(word:str, word_scraped:str):

    start_index = (word.find(word_scraped),word_scraped.find(word))
    append_where = 0 
    # tells caller where extra_letters must be appended (1 end or 2 start)

    l1 = len(word_scraped)
    
    if start_index[0] != -1:
        if start_index[0] == 0:
            extra_letters = word[l1:]
            append_where = 1
        else:
            extra_letters = word[:start_index[0]] + "-" + word[start_index[0]+l1 :]
            append_where = 2
        return (extra_letters,append_where)
     
    if start_index[1] != -1:
        if start_index[1] == 0:
            extra_letters = word_scraped[l1:]
            append_where = 1
        else:
            extra_letters = word_scraped[:start_index[1]] + "-" + word_scraped[start_index[1]+l1 :]
            append_where = 2
        return (extra_letters,append_where)
            
    if start_index == (-1,-1):
        return (-1, append_where)
    


