""" sqlite3 """
import sqlite3

""" if the database doesn't exist, it will be created """
conn = sqlite3.connect('Inverted.db')
print ("Opened database successfully")

cursor = conn.cursor()     

searchWord = input("Enter your search terms: ")
terms = searchWord.split(" ")
print(terms)
  
list_of_URLs = []
for term in terms:
    Query = "SELECT Token, File, Frequency, URL from UCIIndex WHERE Token = '" + term + "'"
    #Execute the query
    cursor = conn.execute(Query)
    #Display the URLs that have the search word
    print("\nBelow are results of the query: ")
    for row in cursor:
        #print for testing, then comment out 
        if row[3] not in list_of_URLs:
            print (row[0], " - ", row[1], "," , row[2])
            print ("URL = ", row[3], "\n")
            list_of_URLs.append(row[3])
   
"""
# This is for just one token
searchWord = "modego"
Query = "SELECT Token, File, Frequency, URL from UCIIndex WHERE Token = '" + searchWord + "'"

#Execute the query
cursor = conn.execute(Query)

#Display the URLs that have the search word 
print("\nBelow are results of the query: ")

for row in cursor:
   #print for testing, then comment out
   print (row[0], " - ", row[1], "," , row[2])
   print ("URL = ", row[3], "\n")
   list_of_URLs.append(row[3])
""" 

conn.close()
