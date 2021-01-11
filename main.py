import requests,os
from datetime import datetime
from pytz import timezone
from math import trunc

def authentication():
    url = "https://gis.protoenergy.com/portal/sharing/rest/generateToken"
    """ payload = { 'client_id': client_id, 'client_secret': client_secret, 'grant_type': 'client_credentials'}"""

    payload = {'f': 'json',
               'username': os.environ.get('PortalUser'),
               'password': os.environ.get('PortalPassword'),
               'client': 'referer',
               'referer': 'https://gis.protoenergy.com/portal',
               'expiration': '21600'
               }
    data = requests.post(url, payload).json()
    token = str(data['token'])
    return token

class terminalsUpdate:
    def __init__(self):
        self.url = "https://geoevent.protoenergy.com/arcgis/rest/services/Hosted/totalLoaded_terminals_Replenishment/FeatureServer"
        self.queryUrl = "/0/query"
        self.update= "/0/updateFeatures"
        self.delete = "/0/deleteFEatures"
        self.token = authentication()
        self.payload = {"f":"json","token":self.token}

    def request(self,url,payload):
        response = requests.request("POST",url,data=payload).json()
        return response

    def deleteFeatures(self,oid):
        url = self.url + self.delete
        payload = self.payload
        payload['where'] = "objectid =" + str(oid)
        response = requests.post(url,payload).json()
        print(response)
        return response

    def getDate(self):
        time_zone = timezone('Africa/Nairobi')
        ke_time = datetime.now(time_zone).strftime("%Y-%m-%d")
        return ke_time

    def epochDate(self,ftime):
        time_epoch = trunc(ftime/1000)
        time_date = datetime.fromtimestamp(time_epoch).strftime('%Y-%m-%d')
        return str(time_date)

    def timeDiff(self,ftime):
        time_zone = timezone('Africa/Nairobi')
        time_now = trunc(datetime.now(time_zone).timestamp())
        time_diff = time_now - trunc(ftime/1000)
        return time_diff


    def query(self):
        query = "1=1"
        #query = 'dateadded =' + repr(self.getDate())
        return query

    def updateFs(self,oid,terminalname):
        url = self.url + self.update
        features = [{"attributes": {"objectid": oid, "terminalname": terminalname}}]
        payload = self.payload
        payload["features"] = str(features)
        response = self.request(url,payload)
        return response

    def queryFS(self):
        url = self.url + self.queryUrl
        payload = self.payload
        payload["where"] = self.query()
        payload["outFields"] = "*"

        response = self.request(url,payload)
        #print(response)
        return response

    def queryResult(self):
        terminals = []
        data = self.queryFS()
        data = data['features']
        for i in data:
            attributes = i["attributes"]
            terminals.append(attributes)

        #print(terminals)
        return terminals

    def terminalUpdate(self):
        data = self.queryResult()
        terminal_list = []
        for i in data:
            if i["terminalname"] == None and i["fromterminalid"] == 45:
                response = self.updateFs(i["objectid"],"Kabati")
                print('updating...')
                #print(response)
                #print({"id":i["objectid"],"terminalname":"Kabati"})

            elif i["terminalname"] == None and i["fromterminalid"] == 105:
                response = self.updateFs(i["objectid"], "Nakuru")
                print('updating..')
                #print(response)
                #print({"id":i["objectid"],"terminalname":"Nakuru"})

            elif i["terminalname"] == None and i["fromterminalid"] == 124:
                response = self.updateFs(i["objectid"], "Amaan")
                #print(response)
                print('updating..')
                #print({"id":i["objectid"],"terminalname":"Amaan"})

            elif i["terminalname"] is not None:
                print("Record updated")
            else:
                print("Matching Error: Id({0})does not match Terminal Name".format(i["objectid"]))

        for k in data:
            if k['dateadded'] == self.getDate() and self.timeDiff(k['timeadded']) > 2000:
                print(k['objectid'],k['dateadded'],self.timeDiff(k['timeadded']),self.getDate())
                response = self.deleteFeatures(k['objectid'])
                print(response)

if __name__ == "__main__":
    terminalsUpdate().terminalUpdate()
