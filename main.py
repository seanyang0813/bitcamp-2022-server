import os
import psycopg2
import hashlib


def exec_statement(conn, stmt):
    try:
        with conn.cursor() as cur:
            cur.execute(stmt)
            # row = cur.fetchall()
            conn.commit()
            # if row: print(row)
            print("worked")
    except psycopg2.ProgrammingError as e:
        print(e)
        print("failed")
        return


def main():
    m = hashlib.sha256()
    word = 'Hello World2'
    m.update(word.encode())
    # Connect to CockroachDB
    connection = psycopg2.connect('postgresql://seanyang0813:bXhti0b3AB4shagATzKsXA@free-tier14.aws-us-east-1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full&options=--cluster%3Djungle-turkey-1158')

    statements = [
        # CREATE the messages table
        "CREATE TABLE posts (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), maker STRING, title STRING, content STRING, hash STRING, post_date TIMESTAMP DEFAULT now(), reveal_date TIMESTAMP DEFAULT now())",
        # INSERT a row into the messages table
        # "INSERT INTO messages2 (message, hash) VALUES ('{}', '{}')".format(word, m.hexdigest()),
        # "SELECT * FROM messages2"
    ]
    for statement in statements:
        print(statement)
        exec_statement(connection, statement)

    # Close communication with the database
    connection.close()


if __name__ == "__main__":
    main()
