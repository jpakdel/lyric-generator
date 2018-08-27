
import boto3
from PyDictionary import PyDictionary
dynamodb = boto3.resource("dynamodb")
proxy_table = dynamodb.Table("Proxy")
word_table = dynamodb.Table("Word")
dictionary=PyDictionary()
def clean_slang(word: str) -> str:
    """Text cleaning for slang words, turns them into proper english"""
    if (word[len(word) - 3:]) == "in\'":
        word = word[:len(word) - 1] + "g"
    else:
        if word[len(word)-1]=='\'':
            word = word[:len(word)-1]
    if (word[len(word) - 2:]) == "in" and is_slang(str(word+"g")) is False:
        word += "g"
    if word == "dawg":
        word = "dog"
    if word == "aint":
        word = 'ain\'t'
    if word == "bangaz":
        word = "bangers"
    if word == "balla":
        word = "baller"
    if word == "blak":
        word = "black"
    if word == "bytches":
        word = "bitches"
    if word == "chu" or word == "u":
        word = "you"
    if word == "choosen":
        word = "choosing"
    if word == "fingaz" or word == "finggaz":
        word = "fingers"
    if word == "fuk":
        word = "fuck"
    if word == "fukin":
        word = "fucking"
    if word == "hamma":
        word = "hammer"
    if word == "im":
        word = "i'm"
    if word == "motha":
        word = "mother"
    if word == "thang":
        word = "thing"
    if word == "ya":
        word = "yeah"
    if word == "somethings":
        word = "something"
    if word == "she's":
        word = "she"
    if word == "shawt":
        word = "shawty"
    if word == "icey":
        word = "icy"
    if word == "gangstaz":
        word = "gangsters"
    if word == "everyone's":
        word = "everyone"
    if word == "finna":
        word = "gonna"
    word = word.replace("β", "b")
    word = word.replace("ι", "i")
    word = word.replace("ε", "e")
    word = word.replace("τ", "t")
    word = word.replace("α", "a")

    return word

ok_slang = [
"your", "you's", "you're", "wanna", "what", "where", "with", "wouldn't", "y'all", "vvs", "twο", "to", "this",
    "them", "these", "they", "the", "that's", "that", "stop", "should", "she's", "phantοm", "ours", "our", "kush",
    "know", "jane", "if", "huh", "house", "how", "her", "good", "got", "gucci", "gotta", "gonna", "gon", "fοr",
    "from", "fleek", "ferrari", "rari", "everything", "dope", "double", "don't", "do", "cοuldn't", "cost",
    "cοngratulatiοns", "cuz", "cuchi", "closed", "come", "cocaine", "bro", "bentley", "because", "aye", "and", "ain't",
    "aquafina", "finna", "she", "of", "off", "out", "cost"
]

def is_slang(word: str):
    """checks to see if word exists """
    if len(word) == 1 and word != 'i' and word != 'a':
        return True
    if hasNumbers(word):
        return True
    for item in ok_slang:
        if word == item:
            return False
    word = word.replace("\'", "")
    return (str(dictionary.meaning(word))[:4]=="None")

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def insert_word(word: str):
    """Inserts all the proper words as individual items into the database and slang words into a list"""

    response = word_table.get_item(
        Key={
            'id': word
        }
    )
    if 'Item' not in response:
        print("{} not in database".format(word))
        word_table.put_item(
            Item={
                'id': word
            }
        )
    else:
        print("{} already in database".format(word))

