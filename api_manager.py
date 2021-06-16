from structs import *

class api_manager:
        def __init__(self,api):
                self.api = api
                self.task_events = []
                self.api.sync()

        def modifyTask(self,event):     
                try:
                        complete = 1 if event.get_completed() else 0
                        item = self.api.items.get_by_id(event.get_Todoid())
                        item.update(content=event.get_name(), due={'date':date_to_str_alternate((event.get_date()))},checked=complete)
                except:
                        self.addTask(event)  # if no task exists to modify simply add it
                return

        def addTask(self,event):
                complete = 1 if event.get_completed() else 0
                task = self.api.items.add(event.get_name(), project_id=self.projId,due={'date':date_to_str_alternate((event.get_date()))})
                
                if(event.get_completed()):
                        task.complete()
                self.task_events.append([task,event])
                return

        def removeTask(self,event):
                try:
                        item = self.api.items.get_by_id(event.get_Todoid())
                        item.delete()
                except:
                        None # if no task exists to remove then do nothing
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
                dbevents = []
                
                items = (self.api.state["items"])
                for item in items:
                        if True:#item["project_id"]==self.projId:
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
                                                        continue # if the dates are wack i am your problem
                                
                                event.data_in(item["content"],date,completed,None,item["id"],None,None,None)
                                events.append(event)

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