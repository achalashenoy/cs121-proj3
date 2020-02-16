import os 
# run only one time to download wordnet and stopwords
'''import nltk
nltk.download('wordnet')
nltk.download('stopwords')'''
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import stopwords

""" to obtain urls from bookkeeping.json"""
import json

""" sqlite3 """
import sqlite3

""" maybe beautiful soup is needed later """
#from bs4 import BeautifulSoup

""" change the path as needed, to load URLs from bookkeeping.json """
with open("C:\WEBPAGES_CLEAN\\bookkeeping.json") as f:
  data = json.load(f)
  
""" if you want to see the data in bookkeeping.json"""
#print(data)


""" tokenize from project 1 """
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

""" compute frequencies from project 1 """
def computeWordFrequencies(the_list):
    frequency = {}        
    for token in the_list:
        count = frequency.get(token, 0)
        frequency[token] = count + 1
    return frequency

""" if you want to test for two files """
#file = "0\\198"
#fileName = "C:\WEBPAGES_CLEAN\\" + file
#tokens = tokenize(fileName)

""" if the database doesn't exist, it will be created """
conn = sqlite3.connect('Inverted.db')
print ("Opened database successfully")

""" IMPORTANT - execute this code one time to create the table, then comment it out """
"""conn.execute('''CREATE TABLE UCIIndex
         (Token           TEXT    NOT NULL,
         File            INT     NOT NULL,
         Frequency       INT     NOT NULL,
         URL             TEXT)''');
"""

cursor = conn.cursor()     

""" Clear the UCIIndex table that had data from the previous run """
cursor = conn.execute("DELETE FROM UCIIndex")

#file = "0/199"
documents_num = 0

the_dict = {}
for subdir, dirs, files in os.walk("C:\WEBPAGES_CLEAN"):
    for f in files:
        documents_num += 1
        filePath = os.path.join(subdir, f)
        tokens = tokenize(filePath)
        """ remove stop words """
        stopWords = set(stopwords.words('english')) 
        filteredTokens = [w for w in tokens if len(w) > 1 if not w in stopWords]
    
        lemmatizer = WordNetLemmatizer() 

        """ lemmatize the date """
        lemmatized = []

        for k in filteredTokens:
        #print(lemmatizer.lemmatize(i) + "\t\t\t" + file)
            lemmatized.append(lemmatizer.lemmatize(k))
        URL = data.get(filePath)
        the_dict.update(computeWordFrequencies(lemmatized))
        """ if you want to see the URL """
        print(filePath)
        print(URL)
        """ If you want to see all the data """
        print(the_dict)
    
        """ to test """
        #print(dict.get('mapping'))
    """ populate the inverted index """
    for key, i in sorted(the_dict.items()):
        #print(key, "\t", file, i, URL)
        conn.execute("INSERT INTO UCIIndex (Token, File, Frequency, URL) \
          VALUES (?, ?, ?, ?)", (key, filePath, i, URL));
    
    """ commit the data """
    conn.commit()

""" The query needs to be inputted by the user from the command line """
searchWord = "machine"
    
Query = "SELECT Token, File, Frequency, URL from UCIIndex WHERE Token = '" + searchWord + "'"
#Query = "SELECT Token, File, Frequency, URL from UCIIndex"

""" Execute the query """
cursor = conn.execute(Query);

""" Display the URLs that have the search word """
print("\nBelow are results of the query: ")
list_of_URLs = []
for row in cursor:
   """ print for testing, then comment out """
   print (row[0], " - ", row[1], "," , row[2])
   print ("URL = ", row[3], "\n")
   list_of_URLs.append(row[3])

""" make sure the program has completed """
print("URLs have been retrieved from the inverted index.")

""" close the database """
conn.close()

def NumOfUniques(a_dict):
    uniques = 0
    for k,v in a_dict.items():
        if v == 1:
            uniques += 1
    return uniques


stats = "# of Documents: " + str(documents_num) + "\n" 
stats += "# of Unique Words: " + str(NumOfUniques(the_dict)) + "\n"
stats += "# of URLs for Query: " + str(len(list_of_URLs)) + "\n"
print(stats)
    
""" test cases for lemmatization """  
#print("rocks :", lemmatizer.lemmatize("stripes")) 
#print("corpora :", lemmatizer.lemmatize("corpora")) 
# a denotes adjective in "pos" 
#print("better :", lemmatizer.lemmatize("better", pos ="a")) 