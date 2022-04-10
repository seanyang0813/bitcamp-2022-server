from flask import Flask, request, jsonify
import psycopg2
import hashlib
import datetime
from flask_cors import CORS
from psycopg2 import sql

app = Flask(__name__)
CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
}, supports_credentials=True)
posts = []

def fetch_statement(conn, stmt):
    try:
        with conn.cursor() as cur:
            cur.execute(stmt)
            row = cur.fetchall()
            conn.commit()
            return row
    except psycopg2.ProgrammingError as e:
        print(e)
        conn.rollback()
        return

def exec_statement(conn, stmt):
    try:
        with conn.cursor() as cur:
            cur.execute(stmt)
            conn.commit()
    except psycopg2.ProgrammingError as e:
        print("error")
        print(e)
        conn.rollback()
        return

connection = psycopg2.connect('postgresql://seanyang0813:bXhti0b3AB4shagATzKsXA@free-tier14.aws-us-east-1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&options=--cluster%3Djungle-turkey-1158')

def add_post(content, title, maker, reveal_date):
    m = hashlib.sha256()
    m.update(content.encode())
    print("new post release date is", reveal_date)
    stmt = sql.SQL("INSERT INTO posts (maker, title, content, hash, reveal_date) VALUES ({}, {}, {}, {}, {})").format(sql.Literal(maker), sql.Literal(title), sql.Literal(content), sql.Literal(m.hexdigest()), sql.Literal(reveal_date))
    exec_statement(connection, stmt)
    return jsonify([])



@app.get("/posts")
def get_posts():
    # query for all of the posts and return them
    stmt = "SELECT * FROM posts"
   
    now = datetime.datetime.utcnow()
    by_user_arg = request.args.get('byuser')
    filter_user = request.args.get('filteruser')
    res = []
    if (filter_user):
        stmt = sql.SQL("SELECT * FROM posts where maker={}").format(sql.Literal(filter_user))
    if (by_user_arg != None):
        stmt = sql.SQL("SELECT * FROM posts LEFT JOIN (select * from post_access where username ={}) as filtered_access ON posts.id = filtered_access.id").format(sql.Literal(by_user_arg))
        if (filter_user):
            stmt = sql.SQL("SELECT * FROM (SELECT * FROM posts LEFT JOIN (select * from post_access where username ={}) as filtered_access ON posts.id = filtered_access.id) where maker={}").format(sql.Literal(by_user_arg), sql.Literal(filter_user))

    fetched = fetch_statement(connection, stmt)
  

    if (by_user_arg != None):
        for x in fetched:
            hidden = False
            if (x[6] > now and x[7] == None and x[1] != by_user_arg):
                hidden = True
            res.append({"id": x[0], "maker": x[1], "title": x[2], "content": None if hidden else x[3], "hash": x[4], "post_date": x[5], "reveal_date": x[6], "paid": True if x[7] != None else False})
    else:
        for x in fetched:
            hidden = False
            if (x[6] > now):
                hidden = True
            print("here")
            res.append({"id": x[0], "maker": x[1], "title": x[2], "content": None if hidden else x[3], "hash": x[4], "post_date": x[5], "reveal_date": x[6], "paid": False})
    # sort res by post_date
    res.sort(key=lambda x: x['post_date'], reverse=True)
    return jsonify(res)

@app.get("/post_access")
def get_access():
    # query for all of the posts and return them
    stmt = "SELECT * FROM post_access"
    fetched = fetch_statement(connection, stmt)
    res = []
    for x in fetched:
        res.append({"id": x[0], "username": x[1]})
    return jsonify(res)

@app.post("/pay")
def pay():
    def unlock_post(user, post_id):
        print(user, post_id)
        #stmt = sql.SQL("INSERT INTO post_access (id, username) VALUES ({}, {})".format(sql.Literal(post_id), sql.Literal(user)))
        stmt = "INSERT INTO post_access (id, username) VALUES ('{}', '{}')".format(post_id, user)
        exec_statement(connection, stmt)
    if request.is_json:

        r = request.get_json()
        if 'username' in r and 'id' in r: 

            print("paying")
            print(r['username'])
            print(r['id'])
            unlock_post(r['username'], r['id'])
            print(r['id'])
            return r['id'], 201
    return {"error": "Request must be JSON"}, 415

@app.post("/post")
def post_post():
    if request.is_json:
        r = request.get_json()
        if 'content' in r and 'title' in r and 'maker' in r and 'reveal_date' in r: 
            res = add_post(r['content'], r['title'], r['maker'], r['reveal_date'])
        return res, 201
    return {"error": "Request must be JSON"}, 415