import os
from tkinter import *
import numpy
import re
# run only one time to download wordnet and stopwords
import nltk
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('words')
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import stopwords
import RetrieveURLs

words = set(nltk.corpus.words.words())
words.add("mondego")

# to obtain urls from bookkeeping.json
import json

# sqlite3 
import sqlite3

# defaultdict for dictionary of lists containing the docs for each token
from collections import defaultdict

# maybe beautiful soup is needed later """
from bs4 import BeautifulSoup

from string import punctuation

# change the path as needed, to load URLs from bookkeeping.json
with open("C:\WEBPAGES\\bookkeeping.json") as f:
  data = json.load(f)
  
# if you want to see the data in bookkeeping.json
#print(data)


# tokenize from project 1
'''This returns a list where the first element is the list of all tokens and the second element is the dictionary of all tagged tokens.'''
def tokenize(fileName):
    file_text = open(fileName, encoding='utf8')
    
    list_of_tokens = []
    list_of_taggeds = []
    list_of_tokens_and_taggeds = []
    dict_of_taggeds = {}
    
    for line in file_text:
        textD = line.encode('ascii', errors='ignore').decode()
        prevChar = ""
        word = ""
        list_of_taggeds.extend(returnlistOfAllTaggedTokens(textD))
        for i in textD:
            if(i.isalnum() == True):
                word += i
            else:   
                if (prevChar.isalnum() != True):
                    continue
                list_of_tokens.append(word.lower())
                word = ""
            prevChar = i
 
        if(len(word) != 0):
            list_of_tokens.append(word.lower())
    convertfromtuptodict(list_of_taggeds, dict_of_taggeds)
    list_of_tokens_and_taggeds.append(list_of_tokens)
    list_of_tokens_and_taggeds.append(dict_of_taggeds)

    return list_of_tokens_and_taggeds

# This will return list of tokens inside HTML tags, in the form of (token, type_of_tag).
# For example, if the text is "<i>apple</i>", the list returned will be [("apple", "i")].
def returnlistOfAllTaggedTokens(the_string):
    list_of_tokens = []
    soup = BeautifulSoup(the_string, "html.parser")
    italicized = soup.find_all('i')
    bolded = soup.find_all('b')
    underlined = soup.find_all('u')
    h1 = soup.find_all('h1')
    h2 = soup.find_all('h2')
    h3 = soup.find_all('h3')
    title = soup.find_all('title')
    all_together = italicized + bolded + underlined + h1 + h2 + h3 + title  
    for i in all_together:
        if i in italicized:
            content =  re.sub("<.*?>", "", str(i))
            list_of_tokens.extend([(token, "i") for token in content.split()])
        if i in bolded:
            content =  re.sub("<.*?>", "", str(i))
            list_of_tokens.extend([(token, "b") for token in content.split()])
        if i in underlined:
            content =  re.sub("<.*?>", "", str(i))
            list_of_tokens.extend([(token, "u") for token in content.split()])
        if i in h1:
            content =  re.sub("<.*?>", "", str(i))
            list_of_tokens.extend([(token, "h1") for token in content.split()])
        if i in h2:
            content =  re.sub("<.*?>", "", str(i))
            list_of_tokens.extend([(token, "h2") for token in content.split()])
        if i in h3:
            content =  re.sub("<.*?>", "", str(i))
            list_of_tokens.extend([(token, "h3") for token in content.split()])        
    return list_of_tokens

'''This turns a list of tuples into a dictionary of key-value pairs.'''
def convertfromtuptodict(the_tuple, the_dict): 
    for k, v in the_tuple: 
        the_dict.setdefault(k, []).append(v) 
    return the_dict 

# compute frequencies from project 1
def computeWordFrequencies(the_list):
    frequency = {}        
    for token in the_list:
        count = frequency.get(token, 0)
        frequency[token] = count + 1
    return frequency

def computeDocsWithWords(a_dict, the_list, docNum):
    for token in the_list:
        a_dict[token].append(docNum)
    return a_dict

# if the database doesn't exist, it will be created
conn = sqlite3.connect('Inverted.db')
print ("Opened database successfully")

# to make the database run faster
conn.execute('pragma journal_mode=OFF')
conn.execute('pragma synchronous=OFF')


# IMPORTANT - execute this code one time to create the table, then comment it out
#conn.execute("DROP TABLE UCIIndex")
conn.execute('''CREATE TABLE UCIIndex
         (Token           TEXT    NOT NULL,
         File            INT     NOT NULL,
         Frequency       INT     NOT NULL,
         IDF             REAL   NULL,
         TF_IDF          REAL   NULL,
         URL             TEXT,
         HTML_weight     INT    NULL)''')

cursor = conn.cursor() 

# Clear the UCIIndex table that had data from the previous run
cursor = conn.execute("DELETE FROM UCIIndex")

documents_num = 0

# the_dict is a dictionary where the keys are tokens and the values are frequencies
# the_dict = {}
token_doc_url_file_tuple_list = []
doc_dict = defaultdict(list)
for subdir, dirs, files in os.walk("C:\WEBPAGES_RAW"):
    for f in files:
        documents_num += 1
        filePath = os.path.join(subdir, f)
        values = tokenize(filePath)
        tokens = values[0]
        taggeds = values[1]
        filePath = subdir[16:] + "/" + f

        # remove stop words
        stopWords = set(stopwords.words('english')) 
        filteredTokens = [w for w in tokens if len(w) > 2 if not w in stopWords]
    
        lemmatizer = WordNetLemmatizer() 

        # lemmatize the date
        lemmatized = []

        for k in filteredTokens:
        #print(lemmatizer.lemmatize(i) + "\t\t\t" + file)
            lemmatized.append(lemmatizer.lemmatize(k))
        # remove non English like zz
        # lemmatized_Engish = " ".join(w for w in lemmatized if w.lower() in words or not w.isalpha())
        lemmatized_Engish = [w for w in lemmatized if w in words ]
        URL = data.get(filePath)
        for l in lemmatized:
            token_doc_url_file_tuple_list.append((l, filePath, documents_num, URL))
            #doc_dict[l].append(documents_num)

        the_dict = computeWordFrequencies(lemmatized)
        doc_dict = computeDocsWithWords(doc_dict, lemmatized, documents_num)
        # if you want to see the URL
        print(filePath)
        weight = 1
        for key, i in sorted(the_dict.items()):
            if ('h1' in taggeds[key] or 'h2' in taggeds[key] or 'h3' in taggeds[key]) and ('b' in taggeds[key] or 'i' in taggeds[key] or 'u' in taggeds[key]):
                weight = 10
            elif ('h1' in taggeds[key] or 'h2' in taggeds[key] or 'h3' in taggeds[key]):
                weight = 9
            elif ('b' in taggeds[key] and 'i' in taggeds[key]) or ('b' in taggeds[key] and 'u' in taggeds[key]) or ('i' in taggeds[key] and 'u' in taggeds[key]):
                weight = 8
            elif ('b' in taggeds[key] or 'i' in taggeds[key] or 'u' in taggeds[key]):
                weight = 7

            conn.execute("INSERT INTO UCIIndex (Token, File, Frequency, URL) \
                VALUES (?, ?, ?, ?)", (key, filePath, i, URL, weight))
    
        # commit the data
        conn.commit()

# Unfortunately updates in any database are very slow and this index has 6 million rows. 
# The work around is to use 3 temp tables as below. All the tables except UCIIndexFinal can be dropped at the end.
# Create table to calculate IDF
print("Creating IDF table")
#conn.execute("DROP TABLE IDF");
conn.execute('''CREATE TABLE IDF
         (Token           TEXT    NOT NULL,
         IDF             REAL   NULL)''')
             
Query = "SELECT Token, COUNT(File) AS IDF FROM UCIIndex GROUP BY Token"
cursor = conn.execute(Query)
for row in cursor:
    conn.execute("INSERT INTO IDF (Token, IDF) \
                VALUES (?, ?)", (row[0], row[1]))
    conn.commit()

# Create table UCIIndexWIthIDF to update with IDF
print("Creating UCIIndexWithIDF because update super slow")
# conn.execute("DROP TABLE UCIIndexWithIDF");
conn.execute('''CREATE TABLE UCIIndexWithIDF
         (Token           TEXT    NOT NULL,
         File            INT     NOT NULL,
         Frequency       INT     NOT NULL,
         IDF             REAL   NULL,
         TF_IDF          REAL   NULL,
         URL             TEXT,
         HTML_weight    INT     NULL)''')
            
Query = "SELECT u.Token, u.File, u.Frequency, i.IDF, TF_IDF, URL FROM UCIIndex u, IDF i WHERE u.Token = i.Token"
cursor = conn.execute(Query)
for row in cursor:
    conn.execute("INSERT INTO UCIIndexWithIDF (Token, File, Frequency, IDF, TF_IDF, URL, HTML_weight) \
                VALUES (?, ?, ?, ?, ?, ?)", (row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
    conn.commit()

print("Creating UCIIndexFinal to update with TF_IDF") 
# conn.execute("DROP TABLE UCIIndexFinal"); 
conn.execute('''CREATE TABLE UCIIndexFinal
         (Token           TEXT    NOT NULL,
         File            INT     NOT NULL,
         Frequency       INT     NOT NULL,
         IDF             REAL   NULL,
         TF_IDF          REAL   NULL,
         URL             TEXT,
         HTML_weight    INT     NULL)''')

Query = "SELECT * from UCIIndexWithIDF"
cursor = conn.execute(Query)
for row in cursor:
    logg = str((1 + numpy.log(row[2])) * numpy.log(37497/row[3]))
    conn.execute("INSERT INTO UCIIndexFinal (Token, File, Frequency, IDF, TF_IDF, URL, HTML_weight) \
                VALUES (?, ?, ?, ?, ?, ?)", (row[0], row[1], row[2], row[3], logg, row[5], row[6]))
    cursor = conn.execute(Query)

    conn.commit()     

# All the temp tables can be dropped at the end
conn.execute("DROP TABLE UCIIndex")
conn.execute("DROP TABLE IDF")
conn.execute("DROP TABLE UCIIndexWithIDF")
 
root = Tk()
root.title("Search Engine")
root.geometry('700x600+100+100')

title_label = Label(root, text="Enter query below")
e = Entry(root)
button = Button(root, text="Search", command = lambda: RetrieveURLs.show_results(e, root))

title_label.grid(row=0, column=0)
e.grid(row=1,column=0)
button.grid(row=2, column=0)
e.delete(0, END)

root.mainloop()

# make sure the program has completed
print("URLs have been retrieved from the inverted index.")

# close the database
conn.close()

def NumOfUniques(a_dict):
    uniques = 0
    for docs in a_dict.values():
        if len(docs) == 1:
            uniques += 1
    return uniques