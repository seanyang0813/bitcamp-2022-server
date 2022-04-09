from flask import Flask, request, jsonify
import psycopg2
import hashlib

app = Flask(__name__)

posts = []

def fetch_statement(conn, stmt):
    try:
        with conn.cursor() as cur:
            cur.execute(stmt)
            row = cur.fetchall()
            conn.commit()
            if row: print(row)
            return row
    except psycopg2.ProgrammingError as e:
        print(e)
        return

def exec_statement(conn, stmt):
    try:
        with conn.cursor() as cur:
            cur.execute(stmt)
            conn.commit()
    except psycopg2.ProgrammingError as e:
        print(e)
        return

connection = psycopg2.connect('postgresql://seanyang0813:bXhti0b3AB4shagATzKsXA@free-tier14.aws-us-east-1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&options=--cluster%3Djungle-turkey-1158')

def add_post(content, title, maker, reveal_date):
    m = hashlib.sha256()
    m.update(content.encode())
    stmt = "INSERT INTO posts (maker, title, content, hash, reveal_date) VALUES ('{}', '{}', '{}', '{}', '{}')".format(maker, title, content, m.hexdigest(), reveal_date)
    exec_statement(connection, stmt)
    return jsonify([])

@app.get("/posts")
def get_countries():
    # query for all of the posts and return them
    stmt = "SELECT * FROM posts"
    fetched = fetch_statement(connection, stmt)
    res = []
    for x in fetched:
        res.append({"id": x[0], "maker": x[1], "title": x[2], "content": x[3], "hash": x[4], "post_date": x[5], "reveal_date": x[6]})
    return jsonify(res)

@app.post("/post")
def add_country():
    if request.is_json:
        r = request.get_json()
        print(r)
        if r['content'] and r['title'] and r['maker'] and r['reveal_date']: 
            print(r['content'])
            res = add_post(r['content'], r['title'], r['maker'], r['reveal_date'])
        return res, 201
    return {"error": "Request must be JSON"}, 415