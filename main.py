import os
import tkinter
import numpy
import re
# run only one time to download wordnet and stopwords
import nltk
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('words')
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import stopwords

words = set(nltk.corpus.words.words())
words.add("mondego")

# to obtain urls from bookkeeping.json
import json

# sqlite3 
import sqlite3

#'''defaultdict for dictionary of lists containing the docs for each token'''
from collections import defaultdict

#""" maybe beautiful soup is needed later """
from bs4 import BeautifulSoup

from string import punctuation

#""" change the path as needed, to load URLs from bookkeeping.json """
with open("C:\WEBPAGES\\bookkeeping.json") as f:
  data = json.load(f)
  
#""" if you want to see the data in bookkeeping.json"""
#print(data)


#""" tokenize from project 1 """
def tokenize(fileName):
    file_text = open(fileName, encoding='utf8')
    
    List = []
    
    for line in file_text:
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

#'''Not sure if this will be a better tokenizer. I tested it out and it LOOKS fine, but you will have to test it more.'''
# def NewTokenize(fileName):
#     file_text = open(fileName, encoding='utf8')
#     list_of_tokens = []
#     final_list = []
#     textD = file_text.encode('ascii', errors='ignore').decode()
#     for line in textD:        
#         soup = BeautifulSoup(line, "html.parser")
#         str_in_tags = [s for s in soup.strings]
#         for s in str_in_tags:
#             list_of_tokens.extend(s.split())
#     for s in list_of_tokens:
#         final_list.append(s.lower().strip(punctuation))
#     return final_list

#'''This will return list of tokens inside HTML tags, in the form of (token, type_of_tag).
#For example, if the text is "<i>apple</i>", the list returned will be [("apple", "i")].''' 
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

#""" compute frequencies from project 1 """
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

#""" if you want to test for two files """
#file = "0\\198"
#fileName = "C:\WEBPAGES_CLEAN\\" + file
#tokens = tokenize(fileName)

#""" if the database doesn't exist, it will be created """
conn = sqlite3.connect('Inverted.db')
print ("Opened database successfully")

conn.execute('pragma journal_mode=OFF')
conn.execute('pragma synchronous=OFF')


#""" IMPORTANT - execute this code one time to create the table, then comment it out """
"""conn.execute('''CREATE TABLE UCIIndex
         (Token           TEXT    NOT NULL,
         File            INT     NOT NULL,
         Frequency       INT     NOT NULL,
         URL             TEXT)''');
"""

# execute this code one time to create the 2-gram table, then comment it out 
# uncomment the drop table as needed
conn.execute("DROP TABLE uciNGramIndex")
conn.execute('''CREATE TABLE uciNGramIndex
         (first_half           TEXT    NOT NULL,
         second_half           TEXT     NOT NULL,
         URL             TEXT,
         Document        TEXT  NOT NULL)''')

cursor = conn.cursor()     

# Clear the UCIIndex table that had data from the previous run
cursor = conn.execute("DELETE FROM UCIIndex")

#file = "0/199
documents_num = 0

# the_dict is a dictionary where the keys are tokens and the values are frequencies
#the_dict = {}
token_doc_url_file_tuple_list = []
doc_dict = defaultdict(list)
for subdir, dirs, files in os.walk("C:\WEBPAGES_RAW"):
    for f in files:
        documents_num += 1
        filePath = os.path.join(subdir, f)
        tokens = tokenize(filePath)
        filePath = subdir[16:] + "/" + f

        #""" remove stop words """
        stopWords = set(stopwords.words('english')) 
        filteredTokens = [w for w in tokens if len(w) > 1 if not w in stopWords]
    
        lemmatizer = WordNetLemmatizer() 

        #"""lemmatize the date """
        lemmatized = []

        for k in filteredTokens:
        #print(lemmatizer.lemmatize(i) + "\t\t\t" + file)
            lemmatized.append(lemmatizer.lemmatize(k))
        # remove non English like zz
        #lemmatized_Engish = " ".join(w for w in lemmatized if w.lower() in words or not w.isalpha())
        lemmatized_Engish = [w for w in lemmatized if w in words ]
        URL = data.get(filePath)
        for l in lemmatized:
            token_doc_url_file_tuple_list.append((l, filePath, documents_num, URL))
            #doc_dict[l].append(documents_num)

        # Below is me finding the 2-grams then adding the 2-grams to the 2-gram table -Jen
        # other_list = lemmatized
        # n_gram = []
        # for i in (range(len(other_list))):
        #     if (len(other_list) <= 1):
        #         break
        #     n_gram.append(other_list[0])
        #     n_gram.append(other_list[1])
        #     other_list = other_list[1:]
        #     conn.execute("INSERT INTO uciNGramIndex (first_half, second_half, URL, Document) \
        #         VALUES (?, ?, ?, ?)", (n_gram[0], n_gram[1], URL, documents_num))
        #     n_gram = []
        the_dict = computeWordFrequencies(lemmatized)
        #the_dict = newComputeWordFrequencies(the_dict, lemmatized)
        doc_dict = computeDocsWithWords(doc_dict, lemmatized, documents_num)
        #"""if you want to see the URL """
        print(filePath)
        #print(URL)
        #""" populate the inverted index """

        for key, i in sorted(the_dict.items()):
        #print(key, "\t", file, i, URL)
            conn.execute("INSERT INTO UCIIndex (Token, File, Frequency, URL) \
                VALUES (?, ?, ?, ?)", (key, filePath, i, URL))
    
        #""" commit the data """
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
#conn.execute("DROP TABLE UCIIndexWithIDF");
conn.execute('''CREATE TABLE UCIIndexWithIDF
         (Token           TEXT    NOT NULL,
         File            INT     NOT NULL,
         Frequency       INT     NOT NULL,
         IDF             REAL   NULL,
         TF_IDF          REAL   NULL,
         URL             TEXT)''')
            
Query = "SELECT u.Token, u.File, u.Frequency, i.IDF, TF_IDF, URL FROM UCIIndex u, IDF i WHERE u.Token = i.Token"
cursor = conn.execute(Query)
for row in cursor:
    conn.execute("INSERT INTO UCIIndexWithIDF (Token, File, Frequency, IDF, TF_IDF, URL) \
                VALUES (?, ?, ?, ?, ?, ?)", (row[0], row[1], row[2], row[3], row[4], row[5]))
    conn.commit()

print("Creating UCIIndexFinal to update with TF_IDF") 
#conn.execute("DROP TABLE UCIIndexFinal"); 
conn.execute('''CREATE TABLE UCIIndexFinal
         (Token           TEXT    NOT NULL,
         File            INT     NOT NULL,
         Frequency       INT     NOT NULL,
         IDF             REAL   NULL,
         TF_IDF          REAL   NULL,
         URL             TEXT)''')

Query = "SELECT * from UCIIndexWithIDF"
cursor = conn.execute(Query)
for row in cursor:
    logg = str((1 + numpy.log(row[2])) * numpy.log(37497/row[3]))
    conn.execute("INSERT INTO UCIIndexFinal (Token, File, Frequency, IDF, TF_IDF, URL) \
                VALUES (?, ?, ?, ?, ?, ?)", (row[0], row[1], row[2], row[3], logg, row[5]))
    cursor = conn.execute(Query)

    conn.commit()     

# All the temp tables can be dropped at the end
#conn.execute("DROP TABLE UCIIndex");
#conn.execute("DROP TABLE IDF");
#conn.execute("DROP TABLE UCIIndexWithIDF");

#""" If you want to see all the data """
#print(the_dict)
#print(len(the_dict))


""" The query needs to be inputted by the user from the command line""" 
#searchWord = 'mondego'
#searchWord = input("Enter your search terms: ")
def show_results():
    search_query = e.get()
    terms = search_query.split(" ")
    list_of_URLs = []
    for term in terms:
        Query = "SELECT Token, File, Frequency, URL from UCIIndex WHERE Token = '" + term + "'"
        """ Execute the query """
        cursor = conn.execute(Query)
        """ Display the URLs that have the search word """
        for row in cursor:
        """ print for testing, then comment out """
            if row[3] not in list_of_URLs:
                print (row[0], " - ", row[1], "," , row[2])
                print ("URL = ", row[3], "\n")
                list_of_URLs.append(row[3])
    offset = 4
    list_of_results = []
    for url in list_of_URLs:
        label = Label(root)
        label["text"] = url 
        list_of_results.append(label)
        label.grid(row=offset, column=0)
        offset += 1

root = Tk()
root.title("Search Engine")
root.geometry('700x600+100+100')

title_label = Label(root, text="Enter query below")
button = Button(root, text="Search", command = show_results)

e = Entry(root)
#title_label.pack()
#e.pack()

title_label.grid(row=0, column=0)
e.grid(row=1,column=0)
button.grid(row=2, column=0)
e.delete(0, END)

root.mainloop()


#Will test this when I get home, probably works but there may be a faster way than executing multiple queries
'''list_of_URLs = []
for term in terms:
    Query = "SELECT Token, File, Frequency, URL from UCIIndex WHERE Token = '" + term + "'"
    """ Execute the query """
    cursor = conn.execute(Query)
    """ Display the URLs that have the search word """
    print("\nBelow are results of the query: ")
    for row in cursor:
        """ print for testing, then comment out """
        if row[3] not in list_of_URLs:
            print (row[0], " - ", row[1], "," , row[2])
            print ("URL = ", row[3], "\n")
            list_of_URLs.append(row[3])
'''
#Query = "SELECT Token, File, Frequency, URL from UCIIndex WHERE Token = '" + searchWord + "'"
#Query = "SELECT Token, File, Frequency, URL from UCIIndex"

#""" Execute the query """
#cursor = conn.execute(Query)

#""" Display the URLs that have the search word """
#print("\nBelow are results of the query: ")
#list_of_URLs = []
#for row in cursor:
#   """ """print for testing, then comment out""" """
#   print (row[0], " - ", row[1], "," , row[2])
#   print ("URL = ", row[3], "\n")
#   list_of_URLs.append(row[3])

#""" make sure the program has completed """
print("URLs have been retrieved from the inverted index.")

#""" close the database """
conn.close()

def NumOfUniques(a_dict):
    uniques = 0
    for docs in a_dict.values():
        if len(docs) == 1:
            uniques += 1
    return uniques

#stats = "# of Documents: " + str(documents_num) + "\n" 
#stats += "# of Unique Words: " + str(NumOfUniques(doc_dict)) + "\n"
#stats += "# of URLs for Query: " + str(len(list_of_URLs)) + "\n"
#stats += str(list_of_URLs[:24]) + "\n"
#print(stats)