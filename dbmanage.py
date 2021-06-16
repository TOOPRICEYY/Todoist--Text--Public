import sys
import os
import argparse
parser = argparse.ArgumentParser()

parser.add_argument("-p", "--pid_file", help="PID file loc")
args = parser.parse_args()
def writePidFile():
  pid = str(os.getpid())
  try:
    os.mkdir(os.path.dirname(args.pid_file))
  except:
   	0
  f = open(args.pid_file, 'w')
  f.write(pid)
  f.close()

import json
import copy
import todoist
import time
import dateparser
from time import sleep
from os import listdir
from difflib import SequenceMatcher
import datetime
from os.path import isfile, join
from parse import parseEntries
from editor import modifier, init_file
from structs import *
from api_manager import api_manager
from nextcloud_api import nextcloud_api
import logging


dir = os.path.dirname(os.path.abspath(__file__))




class main:

    def __init__(self,config):
        
        self.config = config
        self.path = config.get_temp_loc()
        self.pathdb = config.get_db_loc()

        self.api = api_manager(todoist.TodoistAPI(config.get_todoist_api_key()))

        self.db = jsonManager(self.pathdb)

        self.nextcloud = nextcloud_api(config.get_nextcloud_link(),self.path,config.get_nextcloud_user(),config.get_nextcloud_pass()) # nextcloud interfacing api
        all_modded_files = self.nextcloud.pull(self.db.get_files()) # get all files recently modified
        modded_files = all_modded_files[0] # grabs just the modded and added files, omits the negative
        all_modded_files = all_modded_files[0] + all_modded_files[1] # all files edited

        self.fileNames = validFiles([f for f in listdir(self.path) if isfile(join(self.path, f))])
        
        self.dbevents = self.db.getEvents()
        self.edit = modifier(self.fileNames,self.path)
        self.api.setProj('Daily Todo') 
        self.apievents = self.api.getTasks()

        


        temp_fileNames = list(self.fileNames) # This section used to add files with same date as events modified to accurately compare
        for i in modded_files:
            try:
                temp_fileNames.remove(i) # remove all files already known to be modified so doesnt double add
            except:
                None

        

        noRun = True #false and it doesnt run
        fullRun = False
        res = [] # initialized outside of so priming function will always work
        if  noRun and (modded_files!=[] or fullRun):

            

            modded_dates = []
            for m in all_modded_files:
                modded_dates.append(titlestodate([m])[0])
            for m in modded_dates:
                modded_files = modded_files + get_all_files_with_date(m,temp_fileNames)
            
            self.events = parseEntries(modded_files,self.path) # parse only entries modified

            
            
            if fullRun:
                self.events = parseEntries(self.fileNames,self.path) # Parses all files if wanted
                updates = compare(self.events,self.dbevents,self.api) # determine changes made to text document, only compares  events with possibly modified dates 
            else:
                updates = compare(self.events,get_all_events_with_dates(modded_dates,self.dbevents),self.api) # determine changes made to text document, only compares events with possibly modified dates 

            onlyValidAddedTodo = []
            apiRefreshNeeded=False
            for x in updates[0]:
                self.api.addTask(x)
                self.api.commit()
                sleep(.15)
                if(len(str(x.get_Todoid()))>13): # If Api is no longer accepting items
                    apiRefreshNeeded = True
                    for x in onlyValidAddedTodo: # add db events after posting events to Todo to get id's
                        self.db.addEvent(x)
                    self.db.set_files(self.nextcloud.get_curr_mods())
                    self.db.commit()
                    raise Exception("Need to refresh api")

                onlyValidAddedTodo.append(x)
                x.print()
            for x in updates[1]:
                self.api.removeTask(x)
                x.print()
                sleep(.15)
                self.db.removeEvent(x.get_id())
                self.api.commit()
            for x in updates[2]:
                if x.api_change_needed():
                    self.api.modifyTask(x)
                    self.api.commit()
                    sleep(.15)
                x.print()
                self.db.modifyEvent(x)   
                

            for x in updates[0]: # add db events after posting events to Todo to get id's
                self.db.addEvent(x)
            self.db.set_files(self.nextcloud.get_curr_mods())
            self.db.commit()
        
        
        remove_all_events_before_date(self.apievents,config.get_last_day_to_sync()) # stops from syncing long vistigal tasks after clearing out files
        remove_all_events_before_date(self.dbevents,config.get_last_day_to_sync())
        
        updates = compare(self.apievents,self.dbevents,self.api) # determine changes made on Todo 
        

        if  noRun and (not (updates[0] == [] and updates[1] == [] and updates[2] == [])):
            mod = []
            for x in updates[2]:
                if not x.get_archived():
                    self.edit.modifyTask(x,mod)
                sleep(.1)
                self.db.modifyEvent(x) 
            for x in updates[1]:
                self.edit.removeTask(x,mod)
                sleep(.1)
                self.db.removeEvent(x.get_id())    
            for x in updates[0]:
                x = self.edit.addTask(x,mod)
                sleep(.1)
                self.db.addEvent(x)
            
            
            [res.append(x) for x in mod if x not in res] 
            print("Files posting to nextcloud:")
            print(res)
            self.nextcloud.post(res)
            self.db.set_files(self.nextcloud.get_curr_mods()) # update last modified files 
            self.db.commit()

        date = datetime.date.today()
        today = [date.month, date.day, int(str(date.year)[2:4])]

        all_files_in_play = temp_fileNames+modded_files+res

        if noRun and self.db.get_last_prime() != today:
            files_to_prime = get_files_to_be_primed(titlestodate(all_files_in_play), config.get_days_primed()) # files to create in advance
            print("Priming Files: ", files_to_prime)
            for i in files_to_prime:  
                init_file(self.path+i)
            print(get_all_files_with_date(today,all_files_in_play))
            print("files to prime")
            print(files_to_prime)
            
            self.nextcloud.post(files_to_prime)
            print("round 1")
            self.nextcloud.post(get_all_files_with_date(today,all_files_in_play))
            print("next")
            self.db.set_files(self.nextcloud.get_curr_mods())
            self.db.set_last_prime()
            self.db.commit()


        # for event in self.apievents:
        #     self.api.removeTask(event)
        #     self.api.commit()
        #     sleep(.3)
        #     event.print()
       


        
                

    def fs(self, pathfs):
        self.path = pathfs

    def checkForUpdate(self):
        return

    def update(self):
        return
    
    def getTasks(self):
        return self.dbevents
                 

class jsonManager:
    def __init__(self, path): 
        self.path = path
        print(path)
        self.ids = []
        try:
            print("i tried")
            json_file = open(path)
            self.data = json.load(json_file)
            self.data['events']
        except:
            print("and failed")
            f = open(path, "w+")
            f.write(json.dumps({}))
            f.close()
            json_file = open(path)
            self.data = json.load(json_file)
            self.data = {'files':[],'events':[],'dates':[]}
            self.set_last_prime()
        json_file.close()    
        self.getIds()
    

    def set_last_prime(self):
        today = datetime.date.today()
        self.data['dates']= [{'last_prime':dateToStr([today.month, today.day, int(str(today.year)[2:4])])}]

    def get_last_prime(self):
        x = self.data['dates']
        return titlestodate([x[0]['last_prime']])[0]
    

    def set_files(self,files):
        self.data['files'] = []
        for f in files:
            self.data['files'].append({'name':f['name'],'mod':str(f['mod'])})

    def get_files(self):
        files = []
        for f in self.data['files']:
            files.append({'name':f['name'],'mod':dateparser.parse(f['mod'])})
        return files

    def addEvent(self, event):
        id = genId(self.ids)
        self.ids.append(id)
        self.data['events'].append({'line':event.get_line(),'name':event.get_name(),'date':dateToStr(event.get_date()),'completed':event.get_completed(),'description':event.get_description(),'Todoid':event.get_Todoid(),'id':id,'linenums':event.get_linenums(),'archived':event.get_archived()})

    def getEvents(self):
        self.events = []
        for event in self.data['events']:
            temp = Event()
            temp.data_in(event['name'],titlestodate([event['date']])[0],event['completed'],event['description'],event['Todoid'],event['id'],event['line'],event['linenums'])
            temp.set_archived(event['archived'])
            self.events.append(temp)
    
        return self.events

    def removeEvent(self,id):
        for x in self.data['events']:
            if x['id']==id:
                self.ids.remove(id)
                self.data['events'].remove(x)
                break
    
    def modifyEvent(self,event):
        id = event.get_id()
        for x in range(0,len(self.data['events'])):
            if self.data['events'][x]['id']==id:
                self.data['events'][x] = {'line':event.get_line(),'name':event.get_name(),'date':dateToStr(event.get_date()),'completed':event.get_completed(),'description':event.get_description(),'Todoid':event.get_Todoid(),'id':id,'linenums':event.get_linenums(),'archived':event.get_archived()}
                break

    def getIds(self):
        try:
            for event in self.data['events']:
                self.ids.append(event['id'])
        except:
            self.ids =  []
        return self.ids

    def commit(self):
        f = open(self.path, "w")
        f.write(json.dumps(self.data))
        return


def get_files_to_be_primed(dates,amount_to_prime):
    dates = list(dates)
    new_files = []
    for i in range(0,amount_to_prime):
        match = False
        date = datetime.date.today()+datetime.timedelta(days=i)
        date = [date.month, date.day, int(str(date.year)[2:4])]
        for existing_date in dates:
            if existing_date == date:
                dates.remove(existing_date)
                match = True
                break
        if not match:
            new_files.append(dateToStr(date)+".txt")

    return new_files
        
def genId(ids):
    try:
        gen = ids[len(ids)-1]+1
    except:
        gen = 0
    return gen

def compare(events,dbevents,api): # returns array of [pos,neg,mod] changes
    debug = True

    mod = []
    temp = list(events)
    dbevents = list(dbevents)

    switch = False

    if(events != []):
        if events[0].get_Todoid()==None:
            switch = True



    if switch: # if events are text side
        print("Text compare:")
        for event in events:
            for event2 in dbevents:
                if event.get_date() == event2.get_date() and event.get_name() == event2.get_name() and event2.get_linenums()[0] == event.get_linenums()[0]:
                    event.set_Todoid(event2.get_Todoid()) # Assign events db ids
                    event.set_id(event2.get_id())
                    if event.get_completed()!=event2.get_completed() or event.get_description()!=event2.get_description():
                        event.set_edit(get_event_diff(event,event2))
                        mod.append(event)
                        
                    if event.get_completed()!=event2.get_completed() and event2.get_archived(): # if making incomplete and archived unarchive
                        event.set_archived(False)
                    else:
                        event.set_archived(event2.get_archived())

                    dbevents.remove(event2)
                    temp.remove(event)
                    break
        pos=list(temp)
        neg=dbevents
       # print("pos")
        #for n in pos:
        #    n.print()
        #print("neg")
        #for n in neg:
        #    n.print()
            
        for event in temp:
            for event2 in dbevents:
                if event2.get_date()==event.get_date():
                    if event2.get_linenums()[0] == event.get_linenums()[0]: # if events on same line
                        event.set_id(event2.get_id())
                        event.set_Todoid(event2.get_Todoid())
                        event.set_edit(get_event_diff(event,event2))
                        mod.append(event)
                        dbevents.remove(event2)
                        pos.remove(event)
                        break
                    m = SequenceMatcher(None, event.get_name(), event2.get_name())
                    if(m.ratio()>.6): # if events similar
                        event.set_id(event2.get_id())
                        event.set_Todoid(event2.get_Todoid())
                        event.set_edit(get_event_diff(event,event2))
                        mod.append(event)
                        dbevents.remove(event2)
                        pos.remove(event)
                        break
                    if m.ratio()>.3 and abs(event2.get_linenums()[0] - event.get_linenums()[0])<3: # if events less similar but close in line
                        event.set_id(event2.get_id())
                        event.set_Todoid(event2.get_Todoid())
                        event.set_edit(get_event_diff(event,event2))
                        mod.append(event)
                        dbevents.remove(event2)
                        pos.remove(event)
                        break
    else:
        print("api compare:")
        for event in events:
            for dbevent in dbevents:
                if event.get_Todoid() == dbevent.get_Todoid():
                    if not (event.get_date() == dbevent.get_date() and event.get_name() == dbevent.get_name() and event.get_completed()==dbevent.get_completed()): # and event.get_description()==dbevent.get_description()): <- add once description figured out
                        event.set_id(dbevent.get_id())
                        event.set_linenums(dbevent.get_linenums())
                        event.set_description(dbevent.get_description())
                        event.set_edit(get_event_diff(event,dbevent))
                        event.set_archived(False)
                        mod.append(event)
                        if not event.get_date() == dbevent.get_date():
                            event.set_file_change(dbevent.get_date())
                        
                    dbevents.remove(dbevent)
                    temp.remove(event)
                    break

        temp2 = list(dbevents)
        i = 0
        for dbevent in dbevents: # skips already archived events
            if dbevent.get_archived():
                temp2.remove(dbevent)
                i+=1
        dbevents = temp2
        print(str(i)+" Items Skipped Cause Archived")


        temp2 = list(dbevents)
        for dbevent in dbevents: # Checks to see if items were archived
            temper = api.querySingleTask(str(dbevent.get_Todoid()))
            if temper!=None:
                temper.set_id(dbevent.get_id())
                temper.set_linenums(dbevent.get_linenums())
                temper.set_description(dbevent.get_description())
                temper.set_edit(get_event_diff(temper,dbevent))
                print("archived event")
                temper.print()
                temper.set_archived(True)
                if not temper.get_date() == dbevent.get_date():
                            temper.set_file_change(dbevent.get_date())
                mod.append(temper)
                removeItemWithMatchingId(temp2,temper)
                
  


        pos=list(temp)
        neg=temp2


    print("pos")
    for n in pos:
        n.print()
    print("neg")
    for n in neg:
        n.print()
    print("mod")
    for n in mod:
        n.print()
    print()
    return [pos,neg,mod]

def get_event_diff(event, dbevent):
    s = file_change()
    if event.get_date() != dbevent.get_date():
        s.date_edit(True)
    if event.get_name() != dbevent.get_name():
        s.name_edit(True)
    if event.get_completed()!=dbevent.get_completed():
        s.completed_edit(True)
    if event.get_linenums()[0] != dbevent.get_linenums()[0]:
        s.lineNum_edit(True)
    
    return s



config = Config(dir)

#logging.basicConfig(filename=config.get_log_loc(), 
#                    format='%(asctime)s %(levelname)s %(name)s %(message)s')  # commeting out all logging config allows errors to be printed again
#logger=logging.getLogger(__name__)
main(config) 

# try:
#     writePidFile()
#     while True: 
#         start_time = time.time()
        
#         print("--- %s seconds ---" % (time.time() - start_time)) 
#         time.sleep(config.get_refresh_int())
# except Exception as e:
#    logger.error(e)
#    print(e)
#    time.sleep(config.get_refresh_int())
                                 
            
