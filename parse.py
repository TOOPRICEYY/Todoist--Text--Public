import sys
import os
from os import listdir
from os.path import isfile, join
from structs import *


def parseEntries(filesNames, dir):
    dates = titlestodate(filesNames)
    eventList = []
    for i in range(0,len(filesNames)):
        with open(dir+filesNames[i]) as f:
            l = 10
            d = 90
            linenum = 1
            for line in f:
                event = Event()
                event.line_in(line)
                if event.get_state() != False:
                    event.set_date(dates[i])
                    event.set_linenums([linenum,linenum])
                    eventList.append(event)
                    d = linesToChar(line)
                    l = 0
                else:
                    l += 1
                    if l < 4:
                        k = linesToChar(line)
                        #print(eventList[len(eventList)-1].get_line())
                        #print(line)
                        #print(i)
                        if k-d > 1 and k-d < 10:
                            #print("added")
                            b = 0
                            for c in line:
                                if c.isalnum():
                                    break
                                b+=1
                            descript = eventList[len(eventList)-1].get_description()
                            v = 0
                            if line[len(line)-1] == '\n':
                                v = 1
                            if descript != None:
                                descript = str(descript)
                                descript += '\n'+line[b:len(line)-v]
                            else:
                                descript = line[b:len(line)-v]
                            eventList[len(eventList)-1].set_description(descript)
                            arrtemp = eventList[len(eventList)-1].get_linenums()
                            arrtemp[1] = linenum
                            eventList[len(eventList)-1].set_linenums(arrtemp)
                linenum+=1

                    
                    
    return eventList

def linesToChar(line):
    d = 0
    i = 0
    for c in line:
        #print("\'"+c + "\'")
        
        if c == "\t":
            i+=4
        elif c == "\n":
            break
        elif c.isspace():
            i+=1
        elif c.isalnum():
            d = i
            break
    return d

