from flask import Flask, jsonify, render_template, redirect, request 
import pymongo
from bson.json_util import ObjectId
import json


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MyEncoder, self).default(obj)


app = Flask(__name__)
app.json_encoder = MyEncoder

client = pymongo.MongoClient(
    f"mongodb+srv://valentinaba196:informatica4@cluster0.sivkm.mongodb.net/?retryWrites=true&w=majority")
db = client.telescope


@app.route("/getstate")
def index():
    # this will get the first and only element of the configuration collection.
    # it will not include the _id property as it id not necessary
    state = db.configuration.find_one({}, {'_id': False})
    print(state)
    return jsonify(state)


def readAngle(val, vOrH):
    if val == None:
        return None
    try:
        val = float(val) 
    except ValueError:
        # if the value is not a valid number, None will be returned
        return None 

    if vOrH == "v": # if the angle corresponds to a vertical angle 
        # If it is out of bounds it will be modified to be within bounds
        if val < 0:
            val = 0
        if val > 90:
            val = 90
    elif vOrH == "h": # if the angle corresponds to a horizontal angle 
        # If it is out of bounds it will be modified to be within bounds
        if val< 0:
            val=0
        if val> 180:
            val =180
    return val


@app.route("/set")
def setValues():
    # The function readAngle returns None if the value was not received
    # or if it is not a valid number. Otherwise it returns a number within
    # the range admitted by the servos.
    vAngle = readAngle(request.args.get('vAngle'), "v") 
    hAngle = readAngle(request.args.get('hAngle'), "h")

    # If both angles were received
    if vAngle is not None and hAngle is not None:
        print(f"Vertical angle: {vAngle}")
        print(f"Horizontal angle: {hAngle}")
        # the result of the update one operation is stored to check if it was
        # successful
        result=db.configuration.update_one(
            {}, {"$set" : {'hAngle' : hAngle, 'vAngle' : vAngle}})
        #print(result.raw_result)
    # if only the vertical angle is valid 
    elif vAngle is not None:
        db.configuration.update_one({},  {"$set" : {'vAngle' : vAngle}})
        print(f"Vertical angle : {vAngle}")
    # if only the vertical angle is valid
    elif hAngle is not None:
        db.configuration.update_one({},  {"$set" : {'hAngle' : hAngle}})
        print(f"Horizontal angle : {hAngle}")
    # if both angles are invalid
    else:
        print ("Both vertical and horizontal angles are invalid")

    # In any case, the returned values are the ones that are currently in the
    # database

    state = db.configuration.find_one({}, {'_id': False})
    # print(state)
    return jsonify(state)


if __name__ == '__main__':
    app.run(port=5000)
