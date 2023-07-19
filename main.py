from flask import Flask, request, jsonify
import json
import secrets
import pymongo
from pymongo import MongoClient
import os

url = os.getenv('MONGO_URL')
print(url)
client = MongoClient(url)
db = client.virgilUsers
usersCollection = db.users

app = Flask('VirgilAPI')

with open('setting.json', 'r') as f:
    setting = json.load(f)


@app.route('/api/setting/<id>/', methods=['GET'])
def get_user(id):
    result = usersCollection.find_one({"userId": str(id)}, {"_id": 0})
    if result is None:
        return jsonify({"Error": "User not found"}), 404
    print(result["setting"]["volume"])
    return jsonify(result)


@app.route('/api/setting/modify/<string:id>/', methods=['POST'])
def new_setting(id):
    newSetting = request.json
    query = {"userId": str(id)}
    value = {"$set": {'setting': newSetting}}
    result = usersCollection.update_one(query, value)
    return jsonify(newSetting)


@app.route('/api/setting/<string:id>/<string:setting>/<string:subKey>/<string:indexArr>/<value>', methods=['PUT'])
def modify_setting(id, setting, subKey, indexArr, value):
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
    id = secrets.token_hex(16)
    print(id)
    result = usersCollection.insert_one({
        "userId": id,
        "setting": setting
    })
    return jsonify({
        "userId": id,
        "setting": setting
    }), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1111, debug=True)
