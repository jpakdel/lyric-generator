from bs4 import BeautifulSoup
import requests
import boto3
import random

dynamodb = boto3.resource("dynamodb")
proxy_table = dynamodb.Table("Proxy")
word_table = dynamodb.Table("Word")
song_table = dynamodb.Table("Song")
def proxy_scrape():
    """Scrapes sslproxies.org to find proxies to use for other website scraping purposes
     inserts them into DynamoDB table"""
    proxy_list = []
    link = 'https://www.sslproxies.org/'
    script = requests.get(link)
    soup = BeautifulSoup(script.content, 'html.parser')
    try:
        tds = list(soup.find_all("td", {'class': None}))
        for index, val in enumerate(tds):
            if index > 399:
                break
            proxy_list_index = int(index/4)
            current_value = str(tds[index]).replace("<td>", "")
            current_value = current_value.replace("</td>", "")
            if index % 4 == 0:
                proxy_list.append(["",""])
                proxy_list[proxy_list_index][0] = current_value
            elif index % 4 == 1:
                proxy_list[proxy_list_index][1] = current_value
    except AttributeError:
        print("Attribute Error")

    for index, val in enumerate(proxy_list):
        proxy_table.put_item(
            Item={
                'id': str(index),
                'ip': proxy_list[index][0],
                'port': proxy_list[index][1]
            }
        )
    proxy_table.put_item(
        Item={
            'id': "num_proxies",
            'value': str(len(proxy_list))
        }
    )

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

word_dict = []

def dictionary_scrape(word: str):
    """
    This function scrapes definitions from dictionary.com to find the part of speech of a word and inserts it into
    DynamoDB word table.
    :param link, url that we scrape:
    """
    if word[len(word)-3:len(word)] == "ings":
        print("ing")
    else:
        link = "https://www.dictionary.com/browse/{}?s=t".format(word)
        script = requests.get(link)
        soup = BeautifulSoup(script.content, 'html.parser')
        if soup == "" or soup == None:
            print("Using proxy")
            proxy = get_proxy()
            script = requests.get(link, proxies={"http": proxy})
            soup = BeautifulSoup(script.content, 'html.parser')
            print(soup.prettify())
        try:
            part_of_speech = str(list(soup.findAll('span', {'class': "luna-pos"}))[0])
            part_of_speech = part_of_speech.replace("<span class=\"luna-pos\">", "")[0]
            print("{} is a {}".format(word, part_of_speech))
            # word_table.put_item(
            #     Item={
            #         'id': word,
            #         'part_of_speech': part_of_speech
            #     }
            # )
        except IndexError:
            print("{} was not found".format(word))


def genius_scrape(link: str):
    """
    This function scrapes definitions from dictionary.com to find the part of speech of a word and inserts it into
    DynamoDB word table.
    :param link, url that we scrape:
    """
    script = requests.get(link)
    soup = BeautifulSoup(script.content, 'html.parser')
    if soup == "" or soup == None:
        print("Using proxy")
        proxy = get_proxy()
        script = requests.get(link, proxies={"http": proxy})
        soup = BeautifulSoup(script.content, 'html.parser')
    genius_html_list = soup.findAll('meta')
    total_lyrics =[" ", " "]
    for item in genius_html_list:
        blob = str(item)
        #print(blob)
        sample = ""
        found_lyrics = False
        index = 0
        while index < len(blob):
            c = blob[index]
            if index + 6 < len(blob) and blob[index:index+6].lower() == "chorus":
                found_lyrics = True
            elif index + 5 < len(blob) and blob[index:index+5].lower() == "verse":
                found_lyrics = True
            elif index + 4 < len(blob) and blob[index:index+4].lower() == "href":
                found_lyrics = False
            elif index + 4 < len(blob) and blob[index:index+4].lower() == "\\n\\n":
                found_lyrics = False
                index +=3
            if found_lyrics:
                sample += c
            index += 1
        sample = sample.strip()
        if sample!= "":
            sample = lyrics_clean(sample)
            if len(total_lyrics[0]) < len(sample[0]):
                total_lyrics[0] = sample[0]
            if len(total_lyrics[1]) < len(sample[1]):
                total_lyrics[1] = sample[1]
    print("Verse")
    print(total_lyrics[0])
    print("Chorus")
    print(total_lyrics[1])
    insert_song(link, total_lyrics)
def lyrics_clean(blob):
    chorus = False
    verse = False
    index = 0
    chorus_string = ""
    verse_string = ""
    found_lyrics = False
    for index, val in enumerate(blob):
        if index + 6 < len(blob) and blob[index:index + 6].lower() == "chorus":
            chorus = True
            verse = False
            found_lyrics = False
        elif index + 5 < len(blob) and blob[index:index + 5].lower() == "verse":
            verse = True
            chorus = False
            found_lyrics = False
        if val == "&" or val == "(":
            found_lyrics = False
        if index + 2 < len(blob) and blob[index:index + 2].lower() == "\\n":
            found_lyrics = True
        if found_lyrics and chorus:
            chorus_string += val
        if found_lyrics and verse:
            verse_string += val
    verse_string = verse_string.replace("\\n", "$")
    chorus_string = chorus_string.replace("\\n", "$")
    chorus_string = chorus_string.split('[')[0]
    return [verse_string, chorus_string]

def insert_song(link, lyrics):
    """First we update the number of items in the table, then we add an index for which number entry the link is,
    then we finally insert the chorus and verse.
    :param link: str for the url we are scraping lyrics from, becomes unique identifier for the song lyrics
    :param lyrics: str array with two parts, chorus and verse
    :return:
    """
    response = song_table.get_item(
        Key={
            'id': link
        }
    )

    if 'Item' in response:
        print("{} already exists in song table".format(link))
        return

    response = song_table.get_item(
        Key={
            'id': "map"
        }
    )
    map = response['Item']
    print(map)
    try:
        url_list = list(map['url_list'])
        num_items = len(url_list) + 1
        url_list.append(link)
        print("{} is the #{} item in the song table".format(link, str(num_items)))

        update_table(song_table, "map", "url_list", url_list)

        song_table.put_item(
            Item={
                'id': link,
                'chorus': lyrics[1],
                'verse': lyrics[0]
            }
        )
    except KeyError:
        print("Key Error")
    pass

dictionary_scrape("stroking")

def generate_lyrics():
    pass