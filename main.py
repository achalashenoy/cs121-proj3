# -*- coding: utf-8 -*-

# using sqlite3 for database, works well with python and am using it for 125

import nltk
nltk.download('wordnet')
nltk.download('stopwords')
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import stopwords
from urllib.parse import urlparse
from urllib.parse import urljoin
import json

#with open("C:\WEBPAGES_CLEAN\\bookkeeping.json") as f:
#  data = json.load(f)
# Output: {'name': 'Bob', 'languages': ['English', 'Fench']}
#print(data)

# Need to write a loop goes through all the files

# get input.txt
fileName = "input.txt"
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

tokens = tokenize(fileName)

stopWords = set(stopwords.words('english')) 
filteredTokens = [w for w in tokens if not w in stopWords] 
lemmatizer = WordNetLemmatizer() 

for i in filteredTokens:
    print(lemmatizer.lemmatize(i) )
  
# lemmatization
print("rocks :", lemmatizer.lemmatize("stripes")) 
print("corpora :", lemmatizer.lemmatize("corpora")) 
  
# a denotes adjective in "pos" 
print("better :", lemmatizer.lemmatize("better", pos ="a")) 