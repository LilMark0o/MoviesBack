import os
from flask import Flask, jsonify
from flask_mysqldb import MySQL
from dotenv import load_dotenv


app = Flask(__name__)


def connect():
    load_dotenv()
    host = str(os.getenv("HOST"))
    database = str(os.getenv("DATABASE"))
    user = str(os.getenv("USERDB"))
    password = str(os.getenv("PASSWORD"))

    # MySQL configurations
    app.config['MYSQL_HOST'] = host
    app.config['MYSQL_USER'] = user
    app.config['MYSQL_PASSWORD'] = password
    app.config['MYSQL_DB'] = database

    mysql = MySQL(app)
    return mysql


mysql = connect()


@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM genre")
    data = cur.fetchall()
    cur.close()
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
