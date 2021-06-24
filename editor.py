import sys
import os
import copy
from os import listdir
from os.path import isfile, join
from structs import *

class modifier:
    def __init__(self,files,dir):
        self.files = files
        self.dir = dir
        self.dates = titlestodate(self.files)

    def modifyTask(self,event,modified): # modifies event with matching id to contents of event
        name = self.findFile(event.get_date())
        loc = self.dir+name
        if event.get_file_change()!=None:
            mod = copy.deepcopy(event)
            print("Modifying File Loc")
            mod.set_date(mod.get_file_change())
            self.removeTask(mod,modified)
            event = self.addTask(event,modified)
        else:
            add_mod(modified,name)
            with open(loc, "r") as f:
                lines = f.readlines()
            with open(loc, "w+") as f:
                for x in range(0,event.get_linenums()[0]-1):
                    try:
                        f.write(lines[x])
                    except:
                        print("too many changes at once")

                gen_line = event.gen_line()
                f.write('\''+gen_line+' \n')

                x = event.get_linenums()[1]+1
                while x < len(lines):
                    f.write(lines[x])
                    x+=1
                   

                event.set_linenums([event.get_linenums()[0],(event.get_linenums()[0]+amount_of_lines(gen_line)-1)]) # update line numbers

                        


    def addTask(self,even,mod): # adds event returns added event
        event = copy.deepcopy(even)
        name = self.findFile(event.get_date())
        loc = self.dir+name
        add_mod(mod,name)
        if os.path.isfile(loc):
            f = open(loc,"a+")
            f.write('\n\n\''+event.gen_line())
        else:
            f = open(loc,"a+")
            f.write('\''+event.gen_line())
            print(event.gen_line())
        f.close()
        len = file_len(loc)
        event.set_linenums([(len-amount_of_lines(event.gen_line())+1),len])
        return event
        
    def removeTask(self,event,mod): # removes event from list
        name = self.findFile(event.get_date())
        add_mod(mod,name)
        loc = self.dir+name
        try:
            with open(loc, "r") as f:
                lines = f.readlines()
            with open(loc, "w") as f:
                for x in range(0,len(lines)):
                    if (x+1>=event.get_linenums()[0] and x+1<=event.get_linenums()[1]):
                        None
                    elif x==event.get_linenums()[1]:
                        if lines[x][0] != '\n':
                            f.write(lines[x])
                    else:
                        f.write(lines[x])
        except:
            None # if cant delete who cares
                   
        #print(file_len(loc))
        #if file_len(loc)<2:
        #    self.files.remove(name)

    def findFile(self,date): # finds the file name corrisponding to the date or creates new
        for i in range(0,len(self.dates)):
            if self.dates[i]==date:
                return self.files[i]
        name = dateToStr(date)+".txt"
        self.files.append(name)
        self.dates = titlestodate(self.files)
        return name



def init_file(loc):
    f = open(loc,"a+")
    f.close()

def add_mod(mod,name):
    for i in mod:
        if name == i:
            break
    mod.append(name)
