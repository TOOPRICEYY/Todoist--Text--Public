from webdav3.client import Client
import requests
from structs import *
import dateparser
import os
import time
import warnings

warnings.filterwarnings("ignore") 

class nextcloud_api():
    def __init__(self,url,dir,user,pswrd):
        self.url = url
        self.dir = dir
        self.usr = user
        self.pswrd = pswrd
        options = {
        'webdav_hostname': url,
        'webdav_login':    user,
        'webdav_password': pswrd,
        }
        self.client = Client(options)
        self.client.verify = False

    def get_curr_mods(self):
        l =  get_all_valid_files(self.client)
        del l[0] 
        return l

    def pull(self,old_files): # returns all files modified since last time stamp and downloads to local folder
        files = []
        l = get_all_valid_files(self.client)
       
        del l[0] 
        neg = []
        pos = list(l)
        mod = []
        for i in l:
            for f in old_files:
                if i['name'] == f['name']:
                    pos.remove(i)
                    old_files.remove(f)                   
                    if i['mod']>f['mod']:
                        mod.append(i['name'])
                        print("modded ", i)
                        r = requests.get(self.url+i['name'], verify=False, auth=(self.usr, self.pswrd)) # get file contents
                        f = open(self.dir+i['name'],"w+",newline='') 
                        f.write(r.text) # write file contents
                    break
        
        neg = old_files
        for i in pos: # write all added files
            print("pos ",i)
            r = requests.get(self.url+i['name'], verify=False, auth=(self.usr, self.pswrd)) # get file contents
            f = open(self.dir+i['name'],"w+",newline='') 
            f.write(r.text) # write file contents
        
        for i in neg: # delete removed
            print("neg ",i)
            try:
                os.remove(self.dir+i['name'])
            except:
                None
        
        temp = []
        neg_temp = []
        for i in neg: # flatten arrays
            neg_temp.append(i['name'])
        for i in pos:
            temp.append(i['name'])

        files = mod + temp
        print(files)
        # add all file names added/modified/removed, check for date duplicates
        # when scanning in main loops only consider events with same date as in files
        return [files, neg_temp]

    def post(self,files):
        files =  list(files)
        for f in files:
            file = open(self.dir+f,mode='r')
            r = file.read()  
            file.close()
            text = r.encode('latin-1','ignore')
            requests.put(self.url+f, verify=False, data=text,auth=(self.usr, self.pswrd))
            time.sleep(.1)
        temp = files
        compare_time = dateparser.parse("15 seconds ago +00:00")

        while temp!=[]: # validate files were changed
            mods = self.get_curr_mods()
            for f in files:
                for i in mods:
                    if i['name'] == f:
                        if i['mod'] < compare_time:
                            print("file unsent, retrying")
                            file = open(self.dir+f,mode='r')
                            r = file.read()  
                            file.close()
                            text = r.encode('latin-1','ignore')
                            requests.put(self.url+f, verify=False, data=text,auth=(self.usr, self.pswrd))
                            time.sleep(.1)
                        else:
                            temp.remove(f)
                        break

def get_all_valid_files(client):
    files = []
    l = client.list(get_info=True)
    del l[0]
    for i in l:
        if i['isdir'] == False:
            p = i['path'][findFirst(i['path'],"/",False)+1:]
            if is_validFile(p):
                files.append({"name":p,"mod":dateparser.parse(i['modified'])})
    return files
