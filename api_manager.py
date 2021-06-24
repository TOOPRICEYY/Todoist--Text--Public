from structs import *
from collections import defaultdict

class api_manager:
        def __init__(self,api):
                self.api = api
                self.task_events = []
                self.api.sync()
                self.description_events = []
                self.description_cull = []

        def modifyTask(self,event): 
                
                try:
                        complete = 1 if event.get_completed() else 0
                        item = self.api.items.get_by_id(event.get_Todoid())
                        item.update(content=event.get_name(), due={'date':date_to_str_alternate((event.get_date()))},checked=complete)
                        temp = list(event.get_description()) # if having issues with updating id's might be the problem
                        for x in temp: # modify descriptions
                                complete = 1 if x.completed else 0
                                if x.deleted:
                                        try:
                                                item = self.api.items.get_by_id(x.id)
                                                item.delete()
                                                event.get_description().remove(x)
                                        except:
                                                None # already removed
                                elif x.modified:
                                        x.modified = False
                                        item = self.api.items.get_by_id(x.id)
                                        item.update(content=x.text,checked=complete, parent_id=event.get_Todoid())      
                                elif x.id==None:
                                        item = self.api.items.add(x.text, project_id=self.projId, parent_id=event.get_Todoid())
                                        if complete:
                                                item.complete()
                                        self.description_events.append([item,x])

                except:
                        self.addTask(event)  # if no task exists to modify simply add it
                        print("api_manager try may be the cause of your doubling")
                return

        def addTask(self,event):
                
                complete = 1 if event.get_completed() else 0
                task = self.api.items.add(event.get_name(), project_id=self.projId,due={'date':date_to_str_alternate((event.get_date()))})
                if complete:
                        task.complete()
                self.task_events.append([task,event])
                if event.get_description != None: # if there is a description to write
                        self.commit() # grab parent id so can write under
                        for x in event.get_description(): # add descriptions
                                        complete = 1 if x.completed else 0
                                        item = self.api.items.add(x.text, project_id=self.projId, parent_id=event.get_Todoid())
                                        if complete:
                                                item.complete()
                                        self.description_events.append([item,x])

                return

        def removeTask(self,event):
                try:
                        item = self.api.items.get_by_id(event.get_Todoid())
                        item.delete()
                except:
                        None # if no task exists to remove then do nothing
                for x in event.get_description():
                        try:
                                item = self.api.items.get_by_id(x.id)
                                item.delete()
                                event.get_description().remove(x)
                        except:
                                None
                
                return

        def querySingleTask(self, id):
                try:
                        item = self.api.items.get_by_id(id)['item']
                        #print(item)
                        event = Event()   
                        try:
                                completed = True if item["checked"] == 1 else False

                        except:
                                completed = False
                        
                        try:
                                date = Todo_str_to_date(item['due']['date'])
                                #print(item)
                        except:
                                try:
                                        date = Todo_str_to_date(item["due"])
                                        
                                except:
                                        try:
                                                #print(item["due"]["string"])
                                                date = Todo_str_to_date_alternate(item["due"]["string"])
                                        except:
                                                #print(item)
                                                print("Event skipped due to incorrect or non existant date")

                        event.data_in(item["content"],date,completed,None,item["id"],None,None,None)
                except:
                        event = None

                return event

        def getTasks(self):
                events = []
                descriptions = []
                
                items = (self.api.state["items"])
                for item in items:
                        if True:#item["project_id"]==self.projId:
                                event = Event()   
                                try:
                                        completed = True if item["checked"] == 1 else False

                                except:
                                        completed = False
                                
                                try:
                                        date = Todo_str_to_date(item['due']['date'])
                                        #print(item)
                                except:
                                        try:
                                                date = Todo_str_to_date(item["due"])
                                                
                                        except:
                                                try:
                                                        #print(item["due"]["string"])
                                                        date = Todo_str_to_date_alternate(item["due"]["string"])
                                                except:
                                                        if item['parent_id'] != None:
                                                                descript = Description()
                                                                descript.parent_id = item['parent_id']
                                                                descript.text = item['content']
                                                                descript.id = item['id']
                                                                descript.completed = completed
                                                                descriptions.append(descript)
                                                        else:
                                                                print("Event skipped due to incorrect or non existant date")
                                                        continue # if the dates are wack i am your problem
                                #if(item["content"]=="Testies"):
                                #        print(item)
                                event.data_in(item["content"],date,completed,None,item["id"],None,None,None)
                                events.append(event)
                
                if descriptions != []:
                        hash_range = 10
                        count = 0
                        map = [[None] for item in range(hash_range)]
                        for x in descriptions: # hash
                                hash = x.parent_id % hash_range
                                while map[hash][0] != x.parent_id and map[hash][0] != None:
                                        hash=1+hash
                                        if hash>=hash_range:
                                                hash = 0
                                if map[hash][0]:
                                        count+=1                
                                map[hash][0] = x.parent_id
                                map[hash].append(x)
                                #print(map[hash]) 

                        for x in events:
                                hash = x.get_Todoid() % hash_range
                                while map[hash][0] != x.get_Todoid() and map[hash][0] != None:
                                        hash=1+hash
                                        if hash>=hash_range:
                                                hash = 0
                                if map[hash][0] == None:
                                        continue
                                x.set_description(map[hash][1:len(map[hash])])
                                #print("description found")
                                #x.print()
                                if count == 1:
                                        break
                                count-=1
                return events

        def setProj(self,name):
                var = self.api.state['projects']
                id = None
                for proj in var:
                        if proj['name']==name:
                                id = proj['id']
                if id == None:
                        id = self.api.projects.add(name)['id']
                self.projId = id

        def commit(self):
                self.api.commit()
                for [task,event] in self.task_events:
                        event.set_Todoid(task['id'])
                for [task,descript] in self.description_events:
                        descript.id = task['id']
                self.task_events = []
                self.description_events = []


def Todo_str_to_date_alternate(title):
        arr = []
        i = 0
        while title[i] != "-" :
                i+=1
        b = i+1
        month = title[0:i]

        while title[b] != "-":
                b+=1
        day = title[i+1:b]
        i = b+1

        year = title[b+1:]
        arr = [int(month),int(day),int(year)]
        return arr

def Todo_str_to_date(str):
        arr = []
        arr.append(int(str[5:7]))
        arr.append(int(str[8:10]))
        arr.append(int(str[2:4]))
        return arr


def date_to_str_alternate(date):
        m = str(date[0]) if date[0]>9 else "0"+str(date[0])
        d = str(date[1]) if date[1]>9 else "0"+str(date[1])

        return "20"+str(date[2])+"-"+m+"-"+d