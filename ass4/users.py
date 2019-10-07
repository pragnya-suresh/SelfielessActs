#!flask/bin/python
from flask import Flask, jsonify, abort, request,redirect,url_for,json,make_response,render_template
from datetime import datetime
from flask_cors import CORS, cross_origin
import base64
import sqlite3
import os
#import table

app = Flask(__name__)
CORS(app, support_credentials=True)
conn = sqlite3.connect('users.db', check_same_thread=False)
conn.execute("PRAGMA foreign_keys = ON")

c = conn.cursor()
http_counts = 0

@app.route('/api/v1/_count', methods = ['POST','PUT','GET','DELETE'])
@cross_origin(supports_credentials=True)
def get_http_counts():
    global http_counts
    if(request.method=='GET'):
        return_list = [http_counts]
        if(return_list[0] != 0):
            if(request.is_json):
                return json.dumps(return_list),200
            else:
                return json.dumps(return_list),200
        else:
            if(request.is_json):
                return json.dumps(0), 200
            else:
                return json.dumps(0), 200
    if(request.method=='DELETE'):
        http_counts = 0
        return jsonify({}),200

    else:
        return jsonify({}),405

@app.errorhandler(404)
def page_not_found(e):
    http_counts += 1
    
#1. Add user - 201, 400, 405
@app.route('/api/v1/users', methods =['GET','POST','DELETE','PUT'])
@cross_origin(supports_credentials=True)
def add_user():
    global http_counts
    http_counts += 1
    import re
    if(request.method=='POST'):
        if(request.is_json):
            uname = request.json['username']
            pwd = request.json['password']
        else:
            received = json.loads(request.data)
            uname = received['username']
            pwd = received['password']
        if(not(uname) or not(pwd)):
            if(request.is_json):
                return jsonify({}),400
            else:
                return jsonify(status="Fields empty"),400
        print(request.method=="POST")

        u_names = list(c.execute("SELECT username FROM users"))
        u_names = [u_names[i][0] for i in range(0,len(u_names))]
        print(u_names)
        if(uname in u_names):
            if(request.is_json):
                # raise AssertionError('Username Already in Use')
                return jsonify({}), 400

            return jsonify(status="Username Already in Use"),400

        if(len(pwd)!=40):
            if(request.is_json):
                # raise AssertionError('Password must be 40 characters long')
                return jsonify({}), 400
            return jsonify(status="Password must be 40 characters long"),400

        if(not bool(re.match(r"^[abcdefABCDEF0-9]+$",pwd))):
            if(request.is_json):
                # raise AssertionError('Password Must Be in Hex Format')
                return jsonify({}), 400
            return jsonify("Password Must Be in Hex Format") , 400
        user = {
            'username': uname,
            'password': pwd
        }

        c.execute("INSERT into users VALUES(?,?)", (uname, pwd))
        conn.commit()
        if(request.is_json):
            return jsonify({}), 201
        return jsonify(status="Successful"), 201

    elif(request.method=='GET'):
        u_names = list(c.execute("SELECT username FROM users"))
        u_names = [u_names[i][0] for i in range(0,len(u_names))]
        if(len(u_names)==0):
            if(request.is_json):
                print("empty response")
                return jsonify({}),204
            else:
                return jsonify(status="Empty Response"),204
        if(request.is_json):
            return json.dumps(u_names),200
        else:
                #return render_template("categories.html", cat=d)
            return json.dumps(u_names),200

    else:
        return jsonify({}),405

#2. Remove User - 200, 400, 405
@app.route('/api/v1/users/<string:user_name>', methods = ['GET','POST','DELETE','PUT'])
@cross_origin(supports_credentials=True)
def remove_user(user_name):
    global http_counts
    http_counts += 1
    if request.method == 'DELETE':
        uname = user_name
        if(not(uname)):
            if(request.is_json):
                return jsonify({}),400
            else:
                return jsonify(status="Fields empty"),400
        u_names = list(c.execute("SELECT username FROM users"))
        u_names = [u_names[i][0] for i in range(0,len(u_names))]
        if(len(u_names)==0):
            if(request.is_json):
                return jsonify({}), 400
            else:
                return jsonify(status = "No users to delete")
        if(uname not in u_names):
            if(request.is_json):
                # raise AssertionError('User does not exist')
                return jsonify({}), 400
            else:
                return jsonify(status = "User does not exist")
        c.execute("DELETE FROM users WHERE username = ?" ,(uname,))
        conn.commit()
        if(request.is_json):
            return jsonify({}),200
        return jsonify(status = "Successful")
    else:
        return jsonify({}),405


if __name__ == '__main__':
    app.run( debug=False,
             host='0.0.0.0',
             port=80
             )

