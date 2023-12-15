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


@app.route('/movies')
@app.route('/movies/<int:page>')
def get_movies(page: int = None):
    cur = mysql.connection.cursor()
    if page:
        offset = (page - 1) * 10  # Ajuste del offset para páginas basadas en 1
        cur.execute(
            "SELECT * FROM movies ORDER BY score DESC LIMIT 10 OFFSET %s", [offset])
    else:
        cur.execute("SELECT * FROM movies ORDER BY score DESC LIMIT 10")
    data = cur.fetchall()
    cur.close()
    return jsonify(data)


@app.route('/actors')
@app.route('/actors/<int:page>')
def get_actors(page: int = None):
    cur = mysql.connection.cursor()
    if page:
        offset = (page - 1) * 10
        cur.execute(
            "SELECT * FROM actors ORDER BY names DESC LIMIT 10 OFFSET %s", [offset])
    else:
        cur.execute("SELECT * FROM actors ORDER BY names DESC LIMIT 10")
    data = cur.fetchall()
    cur.close()
    return jsonify(data)


@app.route('/movie/<int:movie_id>')
def get_movie(movie_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM movies WHERE id = %s", [movie_id])
    data = cur.fetchall()
    cur.close()
    return jsonify(data)


@app.route('/actor/<int:actor_id>')
def get_actor(actor_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM actors WHERE id = %s", [actor_id])
    data = cur.fetchall()
    cur.close()
    return jsonify(data)


@app.route('/movies/search/<string:query>')
@app.route('/movies/search/<string:query>/<int:page>')
def search_movies(query: str, page: int = None):
    cur = mysql.connection.cursor()
    if page:
        offset = (page - 1) * 10
        cur.execute(
            "SELECT * FROM movies WHERE names LIKE %s ORDER BY score DESC LIMIT 10 OFFSET %s", [f"%{query}%", offset])
    else:
        cur.execute(
            "SELECT * FROM movies WHERE names LIKE %s ORDER BY score DESC LIMIT 10", [f"%{query}%"])
    data = cur.fetchall()
    cur.close()
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
