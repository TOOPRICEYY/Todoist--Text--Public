import os.path
import time
from os import path

class Description:
    def __init__(self):
        self.text = None
        self.id = None
        self.completed = False
        self.deleted = False
        self.modified = False
        self.parent_id =  None
        
    def db_in(self,text,completed,id,parent_id):
        self.text = text
        self.completed = completed
        self.id = id
        self.parent_id = parent_id
        

class Event:
    completed_str = ["done","complete","finish","clapped","postponed","incomplete"]
    
    def __init__(self):
        self.name = None
        self.date = None
        self.time = None
        self.completed = None
        self.description = []
        self.Todoid = None
        self.id = None
        self.modified =  False
        self.line = None
        self.linenums = [None,None]
        self.file_change = None # if file has to be moved
        self.edit = None # what has been changed warrenting modification
        self.archived = False

    def line_in(self, line): # input text line, sets state to false if not a task
        for var in range(0,len(line)):
            if(len(line)>var+1):
                if self.notWhiteSpace(line[var]):
                    if line[var] == '\'':
                        v = 0
                        if line[len(line)-1] == '\n':
                            v = 1
                        self.line = line[var+1:len(line)-v]

                        self.state = True
                        break
                    else:
                        self.state = False
                        break
            else:
                self.state = False
                break

        if self.state:

            self.parseLine(self.line)

    def data_in(self, name, date, completed, description, Todoid, id, line, linenums):
        self.name = name
        self.date = date
        self.completed = completed
        self.description = [] if description==None else description
        self.Todoid = Todoid
        self.id = id
        self.line = line
        self.linenums = linenums

    def add_description_by_line(self,line):
        l = findFirst(line,"-",False)
        self.completed = False
        descript = Description()
        if l != -1:
            temp = line[l+1:len(line)]
            for item in self.completed_str:
                if not temp.find(item)==-1:
                    descript.completed = True
                    index = findFirst(line,"-",False)
                    if(line[index-1]==" "):
                        line = line[0:index-1] # no more done 
                    else:
                        line = line[0:index]
                    break

        descript.text = line.strip()
        self.description.append(descript)
        return

    def append_description(self, item):
        self.description.append(item)

    def notWhiteSpace(self,c):
        if c == '\n' or c == '\t' or c == ' ':
            return False
        else:
            return True
    
    def get_line(self):
        return self.gen_line()

    def print_line(self):
        l = "  edited " + self.edit.get_str() if self.edit != None else ""  
        a = " is archived " if self.archived else ""
        descript = ''
        for i in self.description:
            descript = descript + "\n- " + i.text +  str(" (done)" if i.completed else "") + str(" (deleted)" if i.deleted else "") + str(" (modified)" if i.modified else "") + str(" (id:"+str(i.id)+")" if i.id != None else " (no id)")
        return str(self.name) + "  " + str(dateToStr(self.date)) +"  completed: " + str(self.completed) + "  description: " + descript + "  \nline: " +str(self.linenums) + "  id: " + str(self.id) + "  todoId: " + str(self.Todoid) + a + l

    def print(self):
        print(self.print_line())

    def __str__(self):
        return self.print_line()


    def parseLine(self,line):
        l = findFirst(line,"-",False)
        self.completed = False
        if l != -1:
            temp = line[l+1:len(line)]
            for item in self.completed_str:
                if not temp.find(item)==-1:
                    self.completed = True
                    index = findFirst(line,"-",False)
                    if(line[index-1]==" "):
                        line = line[0:index-1] # no more done 
                    else:
                        line = line[0:index]
                    break
        self.name = line.strip()
        return
    
    def gen_line(self):
        if self.modified:
            self.modified = False
        text = ""
        if self.completed:
            text = " - done"
        initial = True
        for x in self.description:
            if not x.deleted:
                text += "\n\t-" + x.text + (" - done" if x.completed else "")
            

        return self.name + text
        

    def set_file_change(self,f):
        self.file_change  = f
    
    def add_edit(self,f):
        if self.edit != None:
            self.edit.sum(f)
        else:
            self.edit = f

    def get_file_change(self):
        return self.file_change

    def api_change_needed(self):
        return self.edit.api_change_needed()

    def set_edit(self,s):
        self.edit = s
    def set_archived(self,s):
        self.archived = s
    def get_archived(self):
        return self.archived
    def get_state(self):
        return self.state
    def get_name(self):
        return self.name
    def set_name(self,name):
        self.modified = True
        self.name = name
    def get_date(self):
        return self.date
    def set_date(self, date):
        self.modified = True
        self.date = date
    def get_time(self):
        return self.time
    def set_time(self,time):
        self.modified = True
        self.time = time
    def get_completed(self):
        return self.completed
    def set_completed(self, completed):
        self.modified = True
        self.completed = completed
    def get_description(self):
        return self.description
    def set_description(self, description):
        self.modified = True
        self.description = description
    def get_id(self):
        return self.id
    def set_id(self, id):
        self.id = id
    def get_Todoid(self):
        return self.Todoid
    def set_Todoid(self, Todoid):
        self.Todoid = Todoid
    def set_linenums(self,linenums):
        self.linenums = linenums
    def get_linenums(self):
        return self.linenums


def amount_of_lines(txt):
    itter = 1
    for s in txt:
        if s == "\n":
            itter+=1
    return itter

def dateToStr(a):
    try:
        date = str(a[0]) + "-" +str(a[1]) + "-" + str(a[2])
    except:
        date = None
    return date
        
def titlestodate(titles):
    arr = []
    for title in titles:
            i = 0
            while title[i] != "-" :
            
                i+=1
            b = i+1
            month = title[0:i]

            while title[b] != "-":
                b+=1
            day = title[i+1:b]
            i = b+1
            while title[i].isdigit() and len(title)>i+1:
                i+=1
            if not len(title)>i+1:
                i+=1
            year = title[b+1:i]
            arr.append([int(month),int(day),int(year)])
    return arr

class Config:
    def __init__(self,dir):
        self.dir = dir
        self.loc = dir+"/.conf"
        attribute_strs = ["db_loc","temp_loc","todoist_api_key","nextcloud_link","nextcloud_user","nextcloud_pass","refresh_int","log_loc","days_primed", "last_day_to_sync"]
        self.attributes = [None] * len(attribute_strs)
        self.default_text = ""
        for i in attribute_strs: # create default text
            self.default_text+=(i+":*\n")

        if path.exists(self.loc):
            with open(self.loc, "r") as f:
                    lines = f.readlines()      
            for i in lines:
                try:
                    e  = i.index(":")
                except:
                    continue

                for a in range(0,len(attribute_strs)):
                    if attribute_strs[a] == i[0:e]:
                        temp = i[e+1:].strip()
                        if temp == "*":
                            raise Exception("please complete .conf")
                        else:
                            self.attributes[a] = temp                
        else:
            f = open(self.loc,"w+",newline='') 
            f.write(self.default_text)
            raise Exception("please complete .conf")

        for i in self.attributes:
            if i == None:
                raise Exception("please complete .conf")

    def get_db_loc(self):
        if self.attributes[0][0] == ".":
            return self.dir+self.attributes[0][1:]
        return self.self.attributes[0]
    def get_temp_loc(self):
        if self.attributes[1][0] == ".":
            return self.dir+self.attributes[1][1:]
        return self.attributes[1]
    def get_todoist_api_key(self):
        return self.attributes[2]
    def get_nextcloud_link(self):
        return self.attributes[3]
    def get_nextcloud_user(self):
        return self.attributes[4]
    def get_nextcloud_pass(self):
        return self.attributes[5]
    def get_log_loc(self):
        if self.attributes[7][0] == ".":
            return self.dir+self.attributes[7][1:]
        return self.self.attributes[7]
    def get_refresh_int(self):
        return int(self.attributes[6])
    def get_days_primed(self):
        return int(self.attributes[8])
    def get_last_day_to_sync(self):
        return titlestodate([self.attributes[9]])[0]

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def validFiles(files):
    filetemp = []
    for file in files:
        if is_validFile(file):
            filetemp.append(file)
    return filetemp

def is_validFile(file):
    if file[0].isnumeric:
            i = 0
            while file[i] != "-" and i<3:
                if not file[i].isnumeric:
                    return False
                i+=1
            if i>2:
                return False
            b = i+1
            while file[b] != "-" and b<4:
                if not file[b].isnumeric:
                    return False
                b+=1
            if b-i>3:
                return False
            i = b+1
            return True

class file_change():
    def __init__(self):
        self.reset()
    def reset(self):
        self.date = False
        self.completed = False
        self.name = False
        self.lineNum = False
        self.description = False

    def sum(self,f):
        self.date = self.date or f.get_date()
        self.completed = self.completed or f.get_completed()
        self.name = self.name or f.get_name()
        self.lineNum = self.lineNum or f.get_lineNum()
        self.description = self.description or f.get_description()

    def api_change_needed(self):
        if self.date or self.name or self.completed or self.description:
            return True
        return False

    def date_edit(self, f):
        self.date = f
    def get_date(self):
        return self.date
    def name_edit(self, f):
        self.name = f
    def get_name(self):
        return self.name
    def completed_edit(self, f):
        self.completed = f
    def get_completed(self):
        return self.completed
    def lineNum_edit(self, f):
        self.lineNum = f
    def get_lineNum(self):
        return self.lineNum
    def get_description(self):
        return self.description
    def description_edit(self, f):
        self.description = f

    
    def get_str(self):
        s = ""
        if self.date:
            s = "date"
        if self.name:
            if s!="":
                s = s+", name"
            else:
                s = "name"
        if self.completed:
            if s!="":
                s = s+", completion"
            else:
                s = "completion"
        if self.lineNum:
            if s!="":
                s = s+", linenum"
            else:
                s = "linenum"
        if self.description:
            if s!="":
                s = s+", description"
            else:
                s = "description"
        return s

def remove_all_events_before_date(events,date):
    temp_arr =  list(events)    
    for e in temp_arr:
        temp = e.get_date()
        if not (temp[2]>date[2] or (temp[2]==date[2] and temp[0]>date[0]) or (temp[0]==date[0] and temp[1]>=date[1])) :
            events.remove(e)

def removeItemWithMatchingId(events,event):
    for e in events:
        if e.get_id() == event.get_id():
            events.remove(e)
            break
    return events

def get_all_files_with_date(date,files):
    dates = titlestodate(files)
    arr = []
    for i in range(0,len(dates)):
        if dates[i] == date:
            arr.append(files[i])
    return arr

def get_all_events_with_dates(dates,events):
    events =  list(events)
    temp = []
    for event in events:
        for d in dates:
            if event.get_date() == d:
                temp.append(event)
                break

    return temp

class timeCircut():
    def __init__(self):
        self.start_time = 0
        self.banner = ""
        self.enabled = True
    def run(self, run):
        self.enabled = run
    def start(self,text):
        if self.enabled:
            self.banner = text
            self.start_time = time.time()
    def stop(self):
        if self.enabled:
            print("\n"+self.banner+" took %s seconds" % (time.time() - self.start_time)+"\n")


def findFirst(str,f,dir): #dir=true start at beginning, finds first instance matching str in f, indexed at beginning of string
    index = -1
    leng = len(f)
    start = 0 if dir else leng-1 
    step = 1 if dir else -1
    if dir: 
        rang = range(0,len(str)-leng)
    else:
        rang = range(len(str)-1,leng,-1)
    for i in rang:
        if str[i] == f[start]:
            o = step
           
            if abs(o)<leng:
                while str[i+o]==f[start+o]:
                    o+=step
                    if not abs(o)<leng:
                        break
                    

                if(abs(o)==leng):
                    return i if dir else i-leng+1
                else:
                    continue
            else:
                return i
    return index