""" sqlite3 """
import sqlite3
import numpy as np
from numpy import dot
from numpy.linalg import norm
import operator

""" if the database doesn't exist, it will be created """
conn = sqlite3.connect('Inverted.db')
print ("Opened database successfully")

cursor = conn.cursor()     

searchWord = input("Enter your search terms: ")
terms = searchWord.split(" ")
print(terms)
  
list_of_URLs = {}
i = 0
for term in terms:
    q = []
    d = []
    Query = "SELECT Token, File, Frequency, IDF, TF_IDF, URL from UCIIndexFinal WHERE Token = '" + term + "'"
    cursor = conn.execute(Query)
    for row in cursor:
        #print for testing, then comment out 
        #print (row[0], " - ", row[1], row[2], row[3], row[4], row[5], "\n")
        file = row[1]
        URL = row[5]
        if (URL not in list_of_URLs):
            # Comment out after testing
            i = i + 1
            Query = "SELECT Token, IDF, TF_IDF FROM UCIIndexFinal WHERE File = '" + file + "'"
            cursor = conn.execute(Query)
            for row in cursor:
                #print(row[0], row[2])
                d.append(row[2])
                if(row[0] in terms):
                    q.append((1 + np.log10(1)) * np.log10(37497/row[2]))
                     #print("query term position in doc", row[0])
                else:
                    q.append(0)
                
            #print(q)
            #print(d)
            cos_sim = dot(q, d)/(norm(q)*norm(d))
            #print("cosine sim - ", cos_sim, " - ", URL, "\n")
            list_of_URLs[URL] = cos_sim
            print(i)
        #break;

sortedDesc = sorted(list_of_URLs.items(), key=operator.itemgetter(1), reverse=True)[:10]
# Showing cosine similarity for testing, need to show only URLs line by line
print("Retrieved ", i, " URLs")
print("Below are the top 10 results of your query: ", sortedDesc) 


conn.close()
