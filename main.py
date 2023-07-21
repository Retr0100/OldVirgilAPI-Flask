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

app = Flask('VirgilAPI')

#Take the base of setting
with open('setting.json', 'r') as f:
    setting = json.load(f)


@app.route('/api/setting/<id>/', methods=['GET'])
def get_user(id):
    """
        A function to bring the user's setting through the generated key to Virgilio.    
    """
    result = usersCollection.find_one({"userId": str(id)}, {"_id": 0})
    if result is None:
        return jsonify({"Error": "User not found"}), 404
    return jsonify(result)


@app.route('/api/setting/modify/<string:id>/', methods=['POST'])
def new_setting(id):
    """
       This function subwrite all the setting of Virgil specifing the key of user and
       send a payload form json        
    """
    newSetting = request.json
    query = {"userId": str(id)}
    value = {"$set": {'setting': newSetting}}
    result = usersCollection.update_one(query, value)
    return jsonify(newSetting)


@app.route('/api/setting/<string:id>/<string:setting>/<string:subKey>/<string:indexArr>/<value>', methods=['PUT'])
def modify_setting(id, setting, subKey, indexArr, value):
    """
       This function is intended to change only one value of the Virgil setting the only weakness is that you can only change one value at a time in fact it is an obsolete and unused function at the moment its operation is not complex in the url you specify the json path to the file and finally the value 

        ex: key/"key1"/"key2"/"$"/value

        In this example where I have inserted the dollar it means that the key does not have a 3 key and simply only the first two will be considered with the final value this obviously also applies to other lengths 

        max length 3 (this is only for Virgil's own use)
             
    """
    newSetting = usersCollection.find_one({"userId": str(id)}, {"_id": 0})
    if newSetting is None:
        return jsonify({"Error": "User not found"}), 404
    if subKey != '$' and indexArr == '$':
        newSetting["setting"][setting][subKey] = value
    elif subKey != '$' and indexArr != '$':
        newSetting["setting"][setting][subKey][int(indexArr)] = value
    elif subKey == '$' and indexArr == '$':
        newSetting["setting"][setting] = value
    query = {"userId": str(id)}
    value = {"$set": newSetting}
    result = usersCollection.update_one(query, value)
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1111, debug=True)
