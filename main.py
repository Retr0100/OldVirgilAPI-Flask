import datetime
from flask import Flask, request, jsonify
import json
import secrets
from pymongo import MongoClient
import os

#Take the url for connection at the MongoDB
urlMongo = os.getenv('MONGO_URL')


#Init the clien of Mongo
client = MongoClient(urlMongo)

db = client.virgilUsers
usersCollection = db.users
calendarCollection = db.calendarEvent
app = Flask('VirgilAPI')



# ---------- USER FUNCTION ----------
#Take the base of setting
with open('setting.json', 'r') as f:
    setting = json.load(f)

@app.route('/api/setting/<id>/', methods=['GET'])
def get_user(id):
    """
        A function to bring the user's setting through the generated key to Virgilio.    
    """
    result = usersCollection.find_one({"userId": str(id)}, {"_id": 0,"userId":0})
    if result is None:
        return jsonify({"Error": "User not found"}), 404
    return jsonify(result)

def checkEmailPass(list):
    
    for i in list:
        if(i == ""):
            return False

@app.route('/api/setting/modify/<string:id>/', methods=['POST'])
def new_setting(id):
    """
       This function subwrite all the setting of Virgil specifing the key of user and
       send a payload form json and skip the value empty       
    """
    newSetting = request.json
    updates = {}
    for key, value in newSetting.items():
            if(value != ""):
                updates[f"setting.{key}"] = value

    query = {"userId": str(id)}
    value = {"$set": updates}
    result = usersCollection.update_many(query, value)
    return jsonify(newSetting)

@app.route('/api/createUser', methods=['PUT'])
def create_user():
    """
    This function creates a new user which is entered into the database by the simple random key generated randomly and the setting base    
    """
    key = secrets.token_hex(16)
    print(key)
    result = usersCollection.insert_one({
        "userId": key,
        "setting": setting
    })
    
    return jsonify({
        "userId": key,
        "setting": setting
    }), 201


# ---------- CALENDAR FUNCTION ----------

@app.route('/api/calendar/<id>/', methods=['GET'])
def get_Events(id):
    """
        A function to bring the caledar user's through the generated key to Virgilio.    
    """
    result = calendarCollection.find_one({"userId": str(id)}, {"_id": 0,"userId":0}) 
    if result is None:
        return jsonify({"Error": "User not found"}), 404
    return jsonify(result)

@app.route('/api/calendar/createUser/<id>/', methods=['PUT'])
def createUser(id):
    calendarCollection.insert_one({"userId": id}) #Prepare the user for give event
    return id,201

@app.route('/api/calendar/createEvent/<id>/<date>/', methods=['POST'])
def create_event(id,date):
    events = request.json
    result = calendarCollection.find_one({"userId":id},{date:1}) #22-05-2002
    query = {"userId": str(id)}
    if(result is None or date not in result):
        print("USER NOT FOUND")
        value = {"$set": events}
        result = calendarCollection.insert_one(query,value)
    else:
        print("USER FOUND")
        print(events[date])
        value = {"$push": {date: {"$each": events[date]}}}
        result = calendarCollection.update_many(query,value) #Add event
    if result is None:
        return jsonify({"Error": "User not found"}), 404
    return value,201

if __name__ == '__main__':
    app.run(host='1.1.1.1', port=1111, debug=False)
