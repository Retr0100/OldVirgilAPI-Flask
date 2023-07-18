from flask import Flask,request
from flask_restful import Resource, Api,reqparse
import json
import secrets
import pymongo
from pymongo import MongoClient

app = Flask(__name__)


with open('setting.json','r') as f:
            setting = json.load(f)
         
   
class GetUser(Resource):
    def get(self,id):
                                            #query  #campi-desiderati
        result = usersCollection.find_one({"userId" : str(id) }, {"_id":0})
        if(result == None):
            return {"Error": "User not found"}, 404
        print(result["setting"]["volume"]) #take element 
        return result
    

api.add_resource(GetUser, '/api/setting/<id>/')
class ModifySetting(Resource):
    def put(self,id,setting,subKey,indexArr,value): #PER RECUPERARI DATI PIU IN PROFONDITA SEMPLICEMENTE 
        newSetting = usersCollection.find_one({"userId" : str(id) }, {"_id":0})
        if(newSetting == None):
            return {"Error": "User not found"}, 404
        if(subKey != '$' and indexArr == '$'):
            newSetting["setting"][setting][subKey] = value
        elif(subKey != '$' and indexArr != '$'):
            newSetting["setting"][setting][subKey][int(indexArr)] = value
        elif(subKey == '$' and indexArr == '$'):
            newSetting["setting"][setting] = value
        query = {"userId" : str(id) }
        value = {"$set":newSetting}
        result = usersCollection.update_one(query, value)
        return newSetting
    
api.add_resource(ModifySetting, '/api/setting/<string:id>/<string:setting>/<string:subKey>/<string:indexArr>/<value>')


class NewSetting(Resource):
    def post(self,id):
        newSetting = request.json
        query = {"userId" : str(id) }
        value = {"$set": {'setting' : newSetting}}
        result = usersCollection.update_one(query, value)
    
api.add_resource(NewSetting, '/api/setting/modify/<string:id>/')

class CreateUser(Resource):
    def put(self):
        id = secrets.token_hex(16)
        print(id)
        result = usersCollection.insert_one({
            "userId" : id ,
            "setting" : setting
            }) #AGGIUNGE
        return {
            "userId" : id ,
            "setting" : setting
            }, 201
        
api.add_resource(CreateUser, '/api/createUser')


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
