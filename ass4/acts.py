#!flask/bin/python
from flask import Flask, jsonify, abort, request,redirect,url_for,json,make_response,render_template
from datetime import datetime
from flask_cors import CORS, cross_origin
import base64
import sqlite3
import os
import requests
#import table

app = Flask(__name__)
CORS(app, support_credentials=True)
conn = sqlite3.connect('acts.db', check_same_thread=False)
conn.execute("PRAGMA foreign_keys = ON")
c = conn.cursor()
http_counts = 0


def get_act_counts(category):
    c.execute("SELECT category,COUNT(actId) from acts group by category")
    l=c.fetchall()

    d={}
    for ele in l:
        e=list(ele)

        d[e[0]]=e[1]

    return d[category]

@app.errorhandler(404)
def page_not_found(e):
    http_counts += 1


#Get total number of acts
@app.route('/api/v1/acts/count', methods=['GET','POST','DELETE','PUT'])
@cross_origin(supports_credentials=True)
def get_count():
    if(request.method=='GET'):
        cat=c.execute("SELECT  category  FROM categories")
        l1=cat.fetchall()
        count=[0]
        if(len(l1)==0):
            if(request.is_json):
                print("empty response")
                l=[count]
                return json.dumps(list(l[0])),200
            else:
                return jsonify(status="Empty Response"),200
        else:
            catt=c.execute("SELECT DISTINCT category FROM acts")
            l=catt.fetchall()
            if(len(l)>0):
                for ele in l:
                    e=list(ele)
                    count[0]+=get_act_counts(e[0])
                    print(e,count)
            print("count:",count[0])
            l=[count]
            return json.dumps(list(l[0])),200
    else:
        return jsonify({}),405


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



#3.list and add categories
@app.route('/api/v1/categories', methods=['GET','POST','DELETE','PUT'])
@cross_origin(supports_credentials=True)
def get_cats():
    global http_counts
    http_counts += 1
    if(request.method=='GET'):
        cat=c.execute("SELECT  category  FROM categories")
        l1=cat.fetchall()
        if(len(l1)==0):
            if(request.is_json):
                print("empty response")
                return jsonify({}),204
            else:
                return jsonify(status="Empty Response"),204
        else:
            d={}
            for ele in l1:
                e=list(ele)
                d[ele[0]]=0

            catt=c.execute("SELECT category FROM acts")
            l=catt.fetchall()
            if(len(l)>0):

                for ele in l:
                    e=list(ele)
                    d[ele[0]]=get_act_counts(e[0])
                        #if(request.args['type']=='json'):
            if(request.is_json):
                return json.dumps(d),200
            else:
                #return render_template("categories.html", cat=d)
                return json.dumps(d),200

    if(request.method == 'POST'):
        if(request.is_json):
            cat = request.json[0]

        else:
            print("here")
            received = json.loads(request.data)
            print(received)
            cat = received[0]

        print(cat)
        if(cat==""):
            if(request.is_json):
                return jsonify({}),400
            else:
                return jsonify(status="Fields empty"),400

        categories = list(c.execute("SELECT category FROM categories"))
        categories = [categories[i][0] for i in range(0, len(categories))]
        if(cat in categories):
            if(request.is_json):
                # raise AssertionError('Category already exists')
                return jsonify({}), 400
            return jsonify(status = "Category already exists"), 400
        c.execute("INSERT INTO categories VALUES(?)", (cat,))
        conn.commit()
        if(request.is_json):
            return jsonify({}), 201
        return jsonify(status = "Success"), 201
    else:
        return jsonify({}),405


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


#COPPPPY THIS IN THE FILE
#6.List acts for a given category (when total #acts is less than 500)-200,204,405,413
@app.route('/api/v1/categories/<string:cat_name>/acts', methods=['GET','POST','DELETE','PUT'])
@cross_origin(supports_credentials=True)
def get_acts(cat_name):
    global http_counts
    http_counts += 1
    print("illi bantu")
    if(request.method=='GET'):
        if(request.args.get('start') is None or request.args.get('end') is None):
            conn.row_factory = dict_factory
            cur = conn.cursor()
            cur.execute("SELECT actId ,username,timestamp,caption ,upvotes ,imgB64  from acts where category= '%s'" %cat_name)
            l=cur.fetchall()


            print(l) #list of tuples
            if(len(l)>0):
                jsonArr=[]
                for ele in l:
                    jsonArr.append(ele)
                #return array of json objects
                if(request.is_json):
                    return json.dumps(jsonArr),200
                else:
                    return json.dumps(jsonArr)
        #return render_template("acts_for_cat.html", cat=jsonArr)

            if(len(l)>100):
                if(request.is_json):
                    print("acts greater than 100")
                    return jsonify({}),413
                else:
                     return jsonify(status="Number of acts >100"),413
            if(len(l)==0):
                print("Fields empty or wrong format")
                if(request.is_json):
                    # print("Emptyyyyy")
                    return jsonify({}),204
                else:
                    return jsonify(status="Empty Response"),204

        elif(len(request.args.get('start'))>0 and len(request.args.get('end')) ):
            print("get in range")
            #print(request.data,type(request.data))
            startRange=request.args.get('start',type=int)
            endRange=request.args.get('end',type=int)
            print(startRange)
            print(endRange)
            conn.row_factory = dict_factory
            cur = conn.cursor()
            cur.execute("SELECT actId ,username,timestamp,caption ,upvotes ,imgB64  from acts where category= '%s' order by timestamp DESC" %cat_name)
            l=cur.fetchall()
            print(l) #list of tuples
            if(endRange>len(l) or startRange<1 or startRange>endRange or startRange>len(l)):
                if(request.is_json):
                    print("wrong indexes")
                    return jsonify({}),204
                else:
                    return jsonify(status="wrong indexes"),204

            if(len(l)>0):
                jsonArr=[]

                for i in range(startRange-1,endRange):
                    jsonArr.append(l[i])
                #return array of json objects
                if(len(jsonArr)>100):
                    if(request.is_json):
                        print("acts greater that 100")
                        return jsonify({}),413
                    else:
                        return jsonify(status="Number of acts >100"),413
                if(request.is_json):
                    return json.dumps(jsonArr),200
                else:
                    return json.dumps(jsonArr),200

            else:
                if(request.is_json):
                    print("wrong format or field empty")
                    return jsonify({}),204
                else:
                    return jsonify(status="Fields empty or wrong format"),204
    else:
        return jsonify({}),405


#7.List number of acts for a given category- 200,204,405
@app.route('/api/v1/categories/<string:cat_name>/acts/size/',methods=['GET','POST','DELETE','PUT'])
@cross_origin(supports_credentials=True)
def get_num_acts(cat_name):
    global http_counts
    http_counts += 1
    if(request.method=='GET'):
        c.execute("SELECT COUNT(actId) from acts where category= '%s'" %cat_name)
        l=c.fetchall()


        if(len(l)>0 and l[0][0]>0):

            return json.dumps(list(l[0])),200
        else:#if category doesn't exist
            print("Fields empty or wrong format")
            if(request.is_json):

                return jsonify({}),204
            else:
                print("yeah")
                return json.dumps({"status":"Fields empty or wrong format"}),204



    else:
        return jsonify({}),405


def check_encoding(s):
    try:
        if type(sb) == str:
            sb_bytes = bytes(sb, 'ascii')
        elif type(sb) == bytes:
            sb_bytes = sb
        else:
            return 0
        return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
    except Exception:
        return 0


def check_timestamp_format(timestamp):
    try:
        datetime.strptime(timestamp,"%d-%m-%Y:%S-%M-%H")
    except ValueError:
        return 0
    return 1




def check_encoding(sb):
    sb=sb.encode("ascii")
    print(sb,type(sb))
    try:

        if type(sb) == str:
            print("OKAYYY")
            sb_bytes = bytes(sb)
            print("str")
        elif type(sb) == bytes:
            sb_bytes = sb
            print("bytes")
        else:
            print("here1",type(sb))
            return 0
        return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
    except Exception as e:
        print("here2",e)
        return 0


def check_timestamp_format(timestamp):
    try:
        datetime.strptime(timestamp,"%d-%m-%Y:%S-%M-%H")
    except ValueError:
        return 0
    return 1


c = conn.cursor()
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

#11.upload an act-201,400,405
@app.route('/api/v1/acts',methods=['GET','POST','DELETE','PUT'])
@cross_origin(supports_credentials=True)
def upload_act():
    # print(request)
    global http_counts
    http_counts += 1
    if(request.method=='POST'):
        if(request.is_json):
            actId=request.json.get('actId')
            username=request.json.get('username')
            category=request.json.get('categoryName')
            caption=request.json.get('caption')
            timestamp=request.json.get('timestamp')
            imgB64=request.json.get('imgB64')
            upvotes=request.json.get('upvotes')
        else:
            received=json.loads(request.data)
            username=received['username']
            actId=received['actId']
            category=received['categoryName']
            caption=received['caption']
            timestamp=received['timestamp']
            imgB64=received['imgB64']
            upvotes=received['upvotes']
        #print(actId,username,category,caption,timestamp,imgB64)
        if(upvotes or not(actId) or not(username) or not(caption) or not(timestamp) or (check_timestamp_format(timestamp)==0) or not(check_encoding(imgB64)) ):
            if(request.is_json):
                print("wrong format")
                return jsonify({}),400

            else:
                return jsonify(status="Fields empty or wrong format"),400
        #print(actId,username,category,caption,timestamp,imgB64)

        url = "http://3.86.184.220:80/api/v1/users"
        res = requests.get(url).json()
        print("res:",res)
        if(username in res):
            print("yes it is")
            t=(actId,)
            c.execute("SELECT actId from acts where actId=?",t)
            l=c.fetchall()
            if(len(l)>0):
                if(request.is_json):
                    print("id not unique")
                    return jsonify({}),400
                else:
                    return jsonify(status="actId not unique"),400
            t=(category,)
            print(t)
            c.execute("SELECT category from categories where category=?",t)
            l=c.fetchall()
            print(l)
            if(len(l)==0):
                if(request.is_json):
                    print("cat doesnt exist")
                    return jsonify({}),400
                else:
                    return jsonify(status="Category not present"),400

            '''
            t=(username,)
            c.execute("SELECT * FROM users WHERE username=?",t)
            act=c.fetchall()
            #update actid,timestamp,imgB64,caption in db
            if(len(act)==0):
                if(request.is_json):
                    print("not a registered user")
                    return jsonify({}),400
                else:
                    return jsonify(status="You are not a registered user"),400
            '''
            row=(actId,category,timestamp,caption,0,imgB64,username)
            c.execute("INSERT INTO acts VALUES (?,?,?,?,?,?,?)",row)
            conn.commit()
            if(request.is_json):
                return jsonify({}),201
                #return jsonify(status="Successfully added!")
            else:
                print("Task done")
                return jsonify(status="Successful"),201

        elif(request.is_json):
            print("Wrong Username")
            return jsonify({}),400

        else:
            return jsonify(status="Wrong Username"),400
    else:
        return jsonify({}),405


@app.route('/api/v1/acts/<int:actId>',methods=['GET','POST','DELETE','PUT'])
def remove_act(actId):
    global http_counts
    http_counts += 1
    if(request.method=='DELETE'):
        t=(actId,)
        c.execute("SELECT * FROM acts WHERE actId=?",t)
        rows=c.fetchall()
        if(len(rows)==0):
            if(request.is_json):
                return jsonify({}),400
            else:
                return jsonify(status="actId not present"),400
        c.execute("delete from acts where actId=?",t)
        conn.commit()
        if(request.is_json):
            return jsonify({}),200
        else:
            return jsonify(status="Successfully deleted"),200
    else:
        return jsonify({}),405


@app.route('/api/v1/acts/upvote',methods=['GET','POST','DELETE','PUT'])
def upvote():
    http_counts += 1
    if(request.method=='POST'):
        received=json.loads(request.data)
        print(received)
        actId=received[0]
        print(actId)
        t=(actId,)
        c.execute("SELECT upvotes FROM acts WHERE actId=?",t)
        rows=c.fetchall()
        print(rows)
        if(len(rows)==0):
            print("act not present")
            return jsonify({}),400
        tt=(rows[0][0]+1,actId)
        c.execute("update acts set upvotes=? where actId=?",tt)
        conn.commit()
        if(request.is_json):
            return jsonify({}),200
        else:
            message="Likes:"+str(rows[0][0]+1)+"<br>"
            return jsonify(status=message),200
    else:
        #print("here")
        return jsonify({}),405

@app.route('/api/v1/categories/<string:cat_name>', methods = ['POST','PUT','GET','DELETE'])
@cross_origin(supports_credentials=True)
def remove_category(cat_name):
    global http_counts
    http_counts += 1
    if(request.method=='DELETE'):
        print(cat_name)
        category = cat_name
        if(cat_name==""):
            if(request.is_json):
                return jsonify({}), 400
            else:
                return jsonify(status = "Fields Empty"), 400

        if(not(category)):
            if(request.is_json):
                return jsonify({}),400
            else:
                return jsonify(status="Fields empty"),400
        t = (category,)

        cs = list(c.execute("SELECT category from categories"))
        cs = [cs[i][0] for i in range(0,len(cs))]
        print(category)
        print(cs)
        if(len(cs)==0):
            if(request.is_json):
                return jsonify({}), 400
            else:
                return jsonify(status = "No category to delete"),400
        if(category not in cs):
            if(request.is_json):
                # raise AssertionError('category does not exist')
                return jsonify({}), 400
            else:
                return jsonify(status = "Category does not exist"),400

        c.execute('DELETE FROM categories WHERE category = ?',(category, ))
        conn.commit()
        if(request.is_json):
            return jsonify({}),200
        return jsonify(status = "Successful"),200

    else:
        return jsonify({}), 405





if __name__ == '__main__':
     app.run( debug=False,
              host='0.0.0.0',
              port=80
              )
#app.run(debug=True)
