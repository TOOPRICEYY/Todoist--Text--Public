import todoist
import dbmanage
import os




dir_path = os.path.dirname(os.path.realpath(__file__))
api = todoist.TodoistAPI('36fe624a933bc438caf2946456f2f8aaaddb3e09')
dbmanager = dbmanage.main(dir_path+'/examples/',dir_path+'db.json',api)


event = dbmanager.getTasks()[0]
date = "20" + str(event.get_date()[2]) + "-" +str(event.get_date()[0]) + "-" + str(event.get_date()[1])
print(date)

task = api.items.add(event.get_name(), project_id=id,due={'string':date},description="descritption")
if(event.get_completed()):
    task.complete()
item = api.items.get_by_id('4379650341')['item']
print(item)
item.update(content='NewTask1', due={'string': '1-3-5'},checked=0)



api.commit()    
print(item)


    

