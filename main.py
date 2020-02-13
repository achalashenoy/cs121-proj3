# -*- coding: utf-8 -*-

import nltk
#nltk.download('wordnet')
#nltk.download('stopwords')
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import stopwords
from urllib.parse import urlparse
from urllib.parse import urljoin
import json
import sqlite3

from bs4 import BeautifulSoup

with open("C:\WEBPAGES_CLEAN\\bookkeeping.json") as f:
  data = json.load(f)
# Output: {'name': 'Bob', 'languages': ['English', 'Fench']}
#print(data)
URL = data.get('0/198')
print(URL)

def tokenize(fileName):
    file_text = open(fileName)
    
    List = []
    
    for line in file_text:
        #text = file_text.read()
        textD = line.encode('ascii', errors='ignore').decode()        
    
        prevChar = ""
        word = ""
        for i in textD:
            if(i.isalnum() == True):
                word += i
            else:   
                if (prevChar.isalnum() != True):
                    continue
                List.append(word.lower())
                word = ""
            prevChar = i
 
        if(len(word) != 0):
            List.append(word.lower())
            
    return List

def computeWordFrequencies(list):
    frequency = {}        
    for token in list:
        count = frequency.get(token, 0)
        frequency[token] = count + 1
    return frequency

#file = "0\\198"
#fileName = "C:\WEBPAGES_CLEAN\\" + file
#tokens = tokenize(fileName)
file = "0\\199"
fileName = "C:\WEBPAGES_CLEAN\\" + file
tokens = tokenize(fileName)

stopWords = set(stopwords.words('english')) 
filteredTokens = [w for w in tokens if len(w) > 1 if not w in stopWords] 
lemmatizer = WordNetLemmatizer() 

lemmatized = []

for i in filteredTokens:
    #print(lemmatizer.lemmatize(i) + "\t\t\t" + file)
    lemmatized.append(lemmatizer.lemmatize(i))
    
dict = computeWordFrequencies(lemmatized)
print(dict)
print(dict.get('software'))

conn = sqlite3.connect('test.db')
print ("Opened database successfully");

cursor = conn.cursor()     

cursor = conn.execute("DELETE FROM UCIIndex")

for key, i in sorted(dict.items()):
    #print(key, "\t", file, i, URL)
    conn.execute("INSERT INTO UCIIndex (Token, File, Frequency, URL) \
      VALUES (?, ?, ?, ?)", (key, file, i, URL));

conn.commit()

searchWord = "software"
        


cursor = conn.execute("SELECT Token, File, Frequency, URL from UCIIndex WHERE Token = 'software'")
for row in cursor:
   print ("Token = ", row[0])
   print ("File = ", row[1])
   print ("Frequency = ", row[2])
   print ("URL = ", row[3], "\n")

print("bye")

conn.close()


    
  
#print("rocks :", lemmatizer.lemmatize("stripes")) 
#print("corpora :", lemmatizer.lemmatize("corpora")) 
# a denotes adjective in "pos" 
#print("better :", lemmatizer.lemmatize("better", pos ="a")) 