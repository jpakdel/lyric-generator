from bs4 import BeautifulSoup
import requests
import boto3
import random

dynamodb = boto3.resource("dynamodb")
proxy_table = dynamodb.Table("Proxy")
word_table = dynamodb.Table("Word")
song_table = dynamodb.Table("Song")

def get_lyrics_list():
    """returns list of all the song urls we have scraped
    """
    response = song_table.get_item(
        Key={
            'id': "map"
        }
    )
    map = response['Item']
    return list(map["url_list"])

word_list = []

def get_words(link: str):
    response = song_table.get_item(
        Key = {
            'id': link
        }
    )
    item = response['Item']
    chorus = item['chorus']
    verse = item['verse']
    verse = verse.split("$")
    chorus = chorus.split("$")
    chorus_verse = [chorus, verse]
    for thing in chorus_verse:
        for item in thing:
            item = item.strip()
            if len(item) > 0:
                words = item.split(' ')
                for word in words:
                    word = str(word).lower()
                    if len(word)>1:
                        if word[len(word)-1] == ",":
                            word = word[:len(word)-1]
                        if word not in word_list:
                            word_list.append(word)



for link in get_lyrics_list():
    get_words(link)
    print(link)

print(sorted(word_list))