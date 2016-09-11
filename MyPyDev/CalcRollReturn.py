#!/usr/bin/python
import glob
import os, os.path
import sys
import random

def getRandomFile(path):
    """
    Returns a random filename, chosen among the files of the given path.
    """
    files = os.listdir(path)
    index = random.randrange(0, len(files))
    return files[index]

DIR = './data/NAZ'
numFiles = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
#print "Number of files: ",numFiles,". Here is my random number: ",random.randint(1,numFiles)
for x in range(1,10,1):
    randNum = random.randint(1,numFiles)
    overall = 0
    mymax = mymin = total = temp = count = 0
    mymaxfile = myminfile = ""
    #for filename in glob.glob("data/NAZ/*.csv"):
    for x in range(1,randNum,1):
        filename = DIR + "/" + getRandomFile(DIR)
        g=open(filename)
        linecount = sum(1 for line in g)
    #     print filename
        if (linecount > 50):
            #for z in range(1,linecount-1,1):
            for z in range(20,21,1):
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
                minFound = maxFound = 0
                for x in range(1,linecount-z,1):
                    count = count + 1
                    y = x + z
                    temp = ((float(lines[x].split(',')[AdjClose]) - float(lines[y].split(',')[AdjClose]))/float(lines[y].split(',')[AdjClose]))*100
                    total = total + temp
                    if (temp < minFound):
                        minFound = temp
                    if (temp > maxFound):
                        maxFound = temp
                 #   print (lines[x].split(',')[Date]),float(lines[x].split(',')[AdjClose]), (lines[y].split(',')[Date]), float(lines[y].split(',')[AdjClose])
     #           print "CummReturn ", total/count, " Total: ", total," Count: ",count," Z: ",z
        overall = overall + (total/count)
    print "Number of files: ",randNum," Return: ",overall/randNum," Min: ",minFound,"Max: ",maxFound
