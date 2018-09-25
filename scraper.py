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
    proxy_response = "http://" + str(item["ip"]) + ":" + item["port"] + "/"
    #proxy_response = [item["ip"], item["port"]]
    return proxy_response

def update_table(table, id: str, key: str, value: str):
    """Updates user table
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
    response = song_table.get_item(
        Key={
            'id': "map_2"
        }
    )
    map_2 = response['Item']

    try:
        url_list = list(map['url_list'])
        num_items = len(url_list) + 1
        url_list_2 = list(map_2['url_list'])
        num_items += len(url_list_2) + 1
        url_list_2.append(link)
        print("{} is the #{} item in the song table".format(link, str(num_items)))

        update_table(song_table, "map_2", "url_list", url_list_2)

        song_table.put_item(
            Item={
                'id': link,
                'lyrics': lyrics
            }
        )
    except KeyError:
        print("Key Error")
    pass

def contains(string: str, snippet: str)-> bool:
    """check to see if string contains another string"""
    string = string.lower()
    #string)
    snippet= snippet.lower()
    if len(snippet) == 1:
        for i in string:
            if i == snippet:
                return True
        return False
    #print(snippet)
    for i, char in enumerate(string):
        if (i + len(snippet))> (len(string)):
            return False
        snip = string[i:i+len(snippet)]
        if snip == snippet:
            return True


def metro_lyric_scrape(link: str):
    """
    This function scrapes lyrics from a metrolyrics song url and inserts them
    :param link, url that we scrape:
    """
    worked = False
    while worked is False:
        try:
            print("Using proxy")
            proxy = get_proxy()
            script = requests.get(link, proxies={"https": proxy, })
            soup = BeautifulSoup(script.content, 'html.parser')
            worked = True
        except requests.exceptions.ConnectionError:
            worked = False
            pass
    html_lines = str(soup.prettify())
    line = ""
    found_lyrics = False
    viable_lyric = False

    #used to make sure we don't take the introduction from songs, we only want lyrics
    intro_counter = 0
    lyrics= ""
    for c in html_lines:
        line+=c

        if c == "\n":
            line = line.strip()
            print(line)
            if contains(line, "(") or line[0] == "<" or contains(line, "["):
                viable_lyric = False
            else:
                viable_lyric = True
            if found_lyrics and viable_lyric and intro_counter > 1 and len(line) > 0:
                lyrics+=line
                lyrics += "\n"
            if contains(line, "</p>") or contains(line, "[Intro"):
                found_lyrics = False
            if contains(line, "\"verse\""):
                intro_counter +=1
                found_lyrics = True

            line = ""
    lyrics=lyrics.strip()
    print(lyrics)

    if len(lyrics)>0:
        insert_song(link, lyrics)

def metro_url_scrape(link: str):
    """
    This function scrapes song urls from an artist page on metrolyrics.com and calls metro_lyric_scrape for
    :param link, url that we scrape:
    """
    worked = False
    while worked is False:
        try:
            print("Using proxy")
            proxy = get_proxy()
            script = requests.get(link, proxies={"https": proxy,})
            soup = BeautifulSoup(script.content, 'html.parser')
            worked = True
        except requests.exceptions.ConnectionError:
            worked = False
            pass
    html_lines = str(soup.prettify())
    line = ""


    url_list = []
    for c in html_lines:
        if c == "\n" or c == "\"":
            if contains(line, ".html") and contains(line, "-lyrics-") and line[len(line) - 4:] == "html" and contains(line, "explicit") is False and contains(line, "remix") is False:
                url_list.append(line)
            line = ""
        else:
            line += c
    for item in url_list:
        metro_lyric_scrape(item)

