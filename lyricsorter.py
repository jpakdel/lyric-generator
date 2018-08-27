from bs4 import BeautifulSoup
import requests
import boto3
import random
import scraper
import slang_cleaner
from PyDictionary import PyDictionary

dynamodb = boto3.resource("dynamodb")
proxy_table = dynamodb.Table("Proxy")
word_table = dynamodb.Table("Word")
song_table = dynamodb.Table("Song")
dictionary=PyDictionary()
def get_lyrics_list():
    """returns list of all the song urls we have scraped
    """
    response = song_table.get_item(
        Key={
            'id': "map"
        }
    )
    map = response['Item']
    return list(map["url_list"])[0:5]


song_words = []
def get_words(link: str):
    """Gets words from links"""
    response = song_table.get_item(
        Key = {
            'id': link
        }
    )

    item = response['Item']
    lyrics = str(item['lyrics'])
    lyric_list = lyrics.split("\n")

    output_list = []
    print(link)
    for item in lyric_list:
        item = item.replace("?", "")
        item = item.replace(",", "")
        item = item.replace(".", " ")
        item = item.replace("\"", "")
        item = item.replace("-", " ")
        item = item.replace("!", "")
        item = item.lower()

        if item not in output_list and hasNumbers(item) is False and scraper.contains(item, ":") is False:
            #print(item)
            output_list.append(remove_paranthases(item).strip())

    for item in output_list:
        word_lines = item.split(" ")


        #print(word_lines)
        if len(word_lines) > 3:
            for word in word_lines:
                word = str(word).lower()
                if len(word)>0 and scraper.contains(word, "&") is False:
                    if word[0] == '\'':
                        word = word[1:len(word)]
                    word = slang_cleaner.clean_slang(word)
                    if word not in song_words and word != ",":
                        song_words.append(word)



slang_words = []
proper_words = []
def separate_words():
    """separates words into slang and not slang"""
    for word in sorted(song_words):
        slang = slang_cleaner.is_slang(word)
        if slang:
            slang_words.append(word)
        else:
            proper_words.append(word)
        print("{} is {}".format(word, str(slang)))
    print("Words")
    print(proper_words)
    print("Slang")
    print(slang_words)

def insert_words():
    """Inserts all the proper words as individual items into the database and slang words into a list"""
    for word in proper_words:
        response = word_table.get_item(
            Key={
                'id': word
            }
        )
        if 'Item' not in response:
            word_table.put_item(
                Item={
                    'id': word
                }
            )
    response = word_table.get_item(
        Key={
            'id': "slang_words"
        }
    )
    dynamo_slang_words = list(response['Item']['words'])
    for word in slang_words:
        if word not in dynamo_slang_words:
            dynamo_slang_words.append(word)
    scraper.update_table(word_table, "slang_words", "words", sorted(dynamo_slang_words))

def lyric_parse(x: int, y: int):
    """
    Gets the lyrics from multiple songs, puts all their words into a single list, separates them into slang and not slang,
    then puts them into database
    :param x: index of first song lyric we want to get words from
    :param y: index of second song lyric we get lyrics from
    :return:
    """
    song_urls = get_song_url_list()
    while x < y:
        song_url = song_urls[x]
        get_words(song_url)
        x +=1
    separate_words()
    insert_words()
def get_song_url_list():
    response = song_table.get_item(
        Key={
            'id': "map"
        }
    )
    song_url_list = list(response['Item']['url_list'])
    response = song_table.get_item(
        Key={
            'id': "map_2"
        }
    )
    map_2 = list(response['Item']['url_list'])
    for item in map_2:
        song_url_list.append(item)

    return(song_url_list)
sentences = []
def remove_paranthases(input: str):
    output = ""
    found_p = False
    for c in input:
        if c == '(':
            found_p = True
        if found_p is False:
            output+=c
        if c == ")":
            found_p = False
    return output
def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

lyric_parse(10, 30)
