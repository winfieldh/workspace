#!/usr/bin/python
import glob
import os, os.path
import sys
import random
from collections import Counter

overall = overallmin = overallmax = 0 

def getRandomFile(path):
    """
    Returns a random filename, chosen among the files of the given path.
    """
    files = os.listdir(path)
    index = random.randrange(0, len(files))
    return files[index]

DIR = './data/NAZ'
daysToTry = 20
numFiles = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
#print "Number of files: ",numFiles,". Here is my random number: ",random.randint(1,numFiles)
iterations = 100000
minFound = maxFound = 0
returnsList=['0.00']
for x in range(1,iterations,1):
    print x
    filename = DIR + "/" + getRandomFile(DIR) #get random file
    g=open(filename)
    linecount = sum(1 for line in g) #length of file
 #     print filename
    if (linecount > daysToTry * 2):
        #for z in range(1,linecount-1,1):
        startPlace = random.randrange(2,linecount-(daysToTry *2))
        f=open(filename)
        lines=f.readlines()
        Date = 0
        Open = 1
        High = 2
        Low = 3
        Close = 4
        Volume = 5
        AdjClose = 6
        y = 0
        total = temp = 0
        for x in range(startPlace,startPlace + daysToTry,1):
            y = x + daysToTry
#             print x,y,linecount
#             sys.exit("DONE")
            temp = ((float(lines[x].split(',')[AdjClose]) - float(lines[y].split(',')[AdjClose]))/float(lines[y].split(',')[AdjClose]))*100
            returnsList.append(round(temp,0))
            total = total + temp
        
#    print " Return: ",temp/daysToTry
    
#    overall = overall + (temp/daysToTry)
#print "Overall Average Return: ",overall/iterations
print Counter(returnsList).most_common(n=10)