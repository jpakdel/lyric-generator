# -*- coding: utf-8 -*-
"""
Created on Sat Aug 25 17:45:12 2018
This file contains the methods used to scrape info from various online domains
@author: Adm
"""
from bs4 import BeautifulSoup
import requests
import boto3
import helper_methods as helper

dynamodb = boto3.resource("dynamodb", region_name='us-east-1', aws_access_key_id="AKIAJNC2HXMRQQD7XVHQ",
         aws_secret_access_key= "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")

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
 

def b_rhymes_scrape(word: str, num_rhymes):

    """
    This function scrapes the rhymes and near rhymes of a given word from:
        b-rhymes.com
    """

    link = "http://www.b-rhymes.com/rhyme/word/{}".format(word)
    script = requests.get(link)
    soup = BeautifulSoup(script.content, 'html.parser')
    if soup == "" or soup == None:
        print("Using proxy")
        proxy = helper.get_proxy()
        script = requests.get(link, proxies={"http": proxy})
        soup = BeautifulSoup(script.content, 'html.parser')
        print(soup.prettify())
     
        
    try:
        
        # get first num_rhymes rhymes for each word, 
        # if run out of rhymes, throw exception
        for i in range(num_rhymes):

            raw_rhymes = str(list(soup.findAll('td', {'class': "word"}))[i])
            raw_rhymes = raw_rhymes[raw_rhymes.find(">") + 3:]

            if i == 0:
                rhymes = [raw_rhymes[raw_rhymes.find(">") + 1 : raw_rhymes.find("<")]]
            else:
                rhymes.append(raw_rhymes[raw_rhymes.find(">") + 1 : raw_rhymes.find("<")])

 
    except IndexError:
        print("{} was not found".format(word))
        
    finally: 
        try:
            return rhymes 
        except UnboundLocalError:
            print("{} was not found".format(word))
        

def phonetic_scrape(word: str):

    """
    This function gets the phonetic representation of words from dictionary.com
    """

    link = "https://www.dictionary.com/browse/{}?s=t".format(word)
    phonetic = [""]
    script = requests.get(link)
    soup = BeautifulSoup(script.content, 'html.parser')
    if soup == "" or soup == None:
        print("Using proxy")
        proxy = helper.get_proxy()
        script = requests.get(link, proxies={"http": proxy})
        soup = BeautifulSoup(script.content, 'html.parser')
        print(soup.prettify())
            
    try:
        word_scraped = str(list(soup.findAll('h1', {'class': "css-1qbmdpe e1rg2mtf5"}))[0]).lower()
        word_scraped = word_scraped[word_scraped.find(">") + 1: word_scraped[1:].find("<") + 1]
        append_where = 0
        
        if word_scraped != word:
            
            (to_append, append_where) = helper.phonetic_scrape_helper(word,word_scraped)
            if to_append == -1:
                print("Need to fix!")
                raise IndexError
            
           
        raw_phonetic = str(list(soup.findAll('span', {'class': "css-1khtv86 e1rg2mtf2"}))[0])
        counter_phonetic = 0
        new_syllable = False
        
        for i in range(len(raw_phonetic)):
            
            #if there's more than one phonetic representation, take only first
            if raw_phonetic[i] == "," or raw_phonetic[i] == ";":
                break
        
            #identify beggining and end of phonetic sylable
            if (raw_phonetic[i] == ">"):
                next_stop = raw_phonetic[i:].find("<") + i
                
                raw_phonetic, next_stop = helper.update_next_stop(raw_phonetic, next_stop, i)
                    
                syllable = raw_phonetic[i + 1:next_stop]
                
                if syllable == "-":
                    new_syllable = True
                
                if next_stop > i+1 and syllable != "]" and syllable != "[" and syllable != "-":
                        
                    #ensure that each syllable occupies a single entry in list
                    if raw_phonetic[i+1] == "-" or new_syllable:                
                        phonetic.append(syllable)
                        counter_phonetic += 1
                        new_syllable = False
                            
                    else:
                        phonetic[counter_phonetic] = phonetic[counter_phonetic] + syllable 
                                                    
                    #gets rid of special characters
                    phonetic[counter_phonetic] = (phonetic[counter_phonetic]).encode('ascii','ignore').decode('unicode_escape')
                        
                    #format by getting rid of unnecessary symbols.
                    phonetic[counter_phonetic] = helper.phonetic_clean(phonetic[counter_phonetic])
                    
                    # for next iteration, add syllable accordingly
                    if raw_phonetic[next_stop - 1] == "-":
                        new_syllable = True
         
        if append_where == 2:
            phonetic = [to_append] + phonetic
        if append_where == 1:
            phonetic = phonetic + [to_append]
            
        return phonetic, word_scraped
 
    except IndexError:
        print("{} was not found".format(word))
        return -1, -1
    
def slang_translate(word: str):

    """
    """

    link = "https://www.dictionary.com/browse/{}?s=t".format(word)
    script = requests.get(link)
    soup = BeautifulSoup(script.content, 'html.parser')
    if soup == "" or soup == None:
        print("Using proxy")
        proxy = helper.get_proxy()
        script = requests.get(link, proxies={"http": proxy})
        soup = BeautifulSoup(script.content, 'html.parser')
        print(soup.prettify())
        
    try:
        exerpt = str(list(soup.findAll('a', {'class': "css-1t9y0kj e19m0k9k1"}))[0])
        corrected = exerpt[exerpt.find(">")+1:exerpt[1:].find("<")+1]
        return corrected
 
    except IndexError:
        print("{} was not found".format(word))
        return -1
 


         
"""try:
        exerpt = str(list(soup.findAll('p', {'class': "css-mgww5h ehevz041"}))[0])
        print(exerpt)
 
    except IndexError:
        
        try:
            exerpt = str(list(soup.findAll('span', {'class': "css-9sn2pa e10vl5dg6"}))[0])        
            print(exerpt)
        except IndexError:
            
            try:
                # word not found
                exerpt = str(list(soup.findAll('a', {'class': "css-1t9y0kj e19m0k9k1"}))[0])
                return exerpt[exerpt.find(">")+1,exerpt[1:].find("<")]
            
            except:
                print("{} was not found".format(word))
                return -1"""
 




