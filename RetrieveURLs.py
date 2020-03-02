""" sqlite3 """
import sqlite3
import numpy as np
from numpy import dot
from numpy.linalg import norm
import operator
from tkinter import *
import RetrieveURLs

""" if the database doesn't exist, it will be created """
conn = sqlite3.connect('Inverted.db')
print ("Opened database successfully")

cursor = conn.cursor()     

#searchWord = input("Enter your search terms: ")
#terms = searchWord.split(" ")
#print(terms)

def show_results(the_entry, the_root): 
    search_query = the_entry.get()
    terms = search_query.split(" ")
    list_of_URLs = {}
    #i = 0
    N = 37497
    for term in terms:
        q = []
        d = []
        Query = "SELECT Token, File, Frequency, IDF, TF_IDF, URL FROM UCIIndexFinal WHERE Token = '" + term + "' \
            ORDER BY (TF_IDF + HTML_weight) DESC LIMIT 1000"
        cursor = conn.execute(Query)
        for row in cursor:
            #print for testing, then comment out 
            #print (row[0], " - ", row[1], row[2], row[3], row[4], row[5], "\n")
            file = row[1]
            URL = row[5]
            if (URL not in list_of_URLs):       
                # Comment out after testing
                #i = i + 1
                Query = "SELECT Token, IDF, TF_IDF, HTML_weight FROM UCIIndexFinal WHERE File = '" + file + "'"
                cursor = conn.execute(Query)
                
                for row in cursor:
                    #print(row[0], row[2])
                    #d.append(row[2])
                    if(row[0] in terms):
                        # TD_IDF and HTML_weight of the query term in the document vector
                        d.append(row[2] + row[3])
                        
                        # TD_IDF of the query term in the query vector
                        q.append((1 + np.log10(1)) * np.log10(N/(row[2])))
                        #print("query term position in doc", row[0])
                    #else:
                        #q.append(0)
                
            #print(q)
            #print(d)
            cos_sim = dot(q, d)/(norm(q)*norm(d))
            #print("cosine sim - ", cos_sim, " - ", URL, "\n")
            list_of_URLs[URL] = cos_sim
            #print(i)
        #break;
    offset = 4
    header = Label(the_root)
    header["text"] = "Below are the results of the top 10 queries"
    header.grid(row=offset, column=0)
    offset += 1
    list_of_results = []
    sortedDesc = sorted(list_of_URLs.items(), key=operator.itemgetter(1), reverse=True)[:10]
    for url in sortedDesc:
        label = Label(the_root, anchor = "w", width = 70)
        label["text"] = url[0]
        list_of_results.append(label)
        label.grid(row=offset, column=0, padx = 50)
        offset += 1

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

#sortedDesc = sorted(list_of_URLs.items(), key=operator.itemgetter(1), reverse=True)[:10]
# Showing cosine similarity for testing, need to show only URLs line by line
#print("Retrieved ", i, " URLs")
#print("Below are the top 10 results of your query: ", sortedDesc) 


conn.close()
