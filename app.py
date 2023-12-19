import os
from pprint import pprint
from flask import Flask, jsonify
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from flask_cors import CORS  # Import the CORS module
from collections import OrderedDict
from time import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

movieStructure = ["id", "name", "date",
                  "score", "overview", "budget", "revenue", "country", "image"]

actorStructure = ["id", "name", "image"]

genreStructure = ["id", "name"]


def makeADict(structure, data):
    return list(map(lambda movie: OrderedDict((structure[i], movie[i]) for i in range(len(structure))), data))


def connect():
    time1 = time()
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
    app.config['MYSQL_PORT'] = 3306

    mysql = MySQL(app)
    time2 = time()
    print(f"Tiempo de conexión: {time2 - time1}")
    return mysql


mysql = connect()


@app.route('/movies')
@app.route('/movies/<int:page>')
def get_movies(page: int = None):
    timeStart = time()
    cur = mysql.connection.cursor()
    if page:
        offset = (page - 1) * 10  # Ajuste del offset para páginas basadas en 1
        cur.execute(
            "SELECT * FROM movies ORDER BY score DESC LIMIT 10 OFFSET %s", [offset])
    else:
        cur.execute("SELECT * FROM movies ORDER BY score DESC")
    data = cur.fetchall()

    newData = makeADict(movieStructure, data)
    cur.close()
    timeEnd = time()
    print(f"Tiempo de ejecución: {timeEnd - timeStart}")
    return jsonify(newData)


@app.route('/actors')
@app.route('/actors/<int:page>')
def get_actors(page: int = None):
    timeStart = time()
    cur = mysql.connection.cursor()
    if page:
        offset = (page - 1) * 10
        cur.execute(
            "SELECT * FROM actors ORDER BY names ASC LIMIT 10 OFFSET %s", [offset])  # Assuming 'names' should be 'name'
    else:
        # Assuming 'names' should be 'name'
        cur.execute("SELECT * FROM actors ORDER BY names ASC")
    data = cur.fetchall()
    cur.close()
    newData = makeADict(actorStructure, data)
    timeEnd = time()
    print(f"Tiempo de ejecución: {timeEnd - timeStart}")
    return jsonify(newData)


@app.route('/movies/id/<int:movie_id>')
def get_movie(movie_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM movies WHERE id = %s", [movie_id])
    data = cur.fetchall()
    cur.close()
    newData = list()
    for movie in data:
        movieDict = OrderedDict()
        for i in range(len(movieStructure)):
            movieDict[movieStructure[i]] = movie[i]
        newData.append(movieDict)
    cur.close()
    return jsonify(movieDict)


@app.route('/movies/id/<int:movie_id>/actors')
def get_actorByMovie(movie_id):
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT actors.* FROM actors JOIN moviesActors ON actors.id = moviesActors.actor_id JOIN movies ON movies.id = moviesActors.movie_id WHERE movies.id = %s", [movie_id])
    data = cur.fetchall()
    cur.close()
    newData = makeADict(actorStructure, data)
    cur.close()
    return jsonify(newData)


@app.route('/actors/<int:actor_id>/movies')
def get_moviesByActor(actor_id):
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT movies.* FROM movies JOIN moviesActors ON movies.id = moviesActors.movie_id JOIN actors ON actors.id = moviesActors.actor_id WHERE actors.id = %s", [actor_id])
    data = cur.fetchall()
    cur.close()
    new_data = makeADict(movieStructure, data)
    return jsonify(new_data)


@app.route('/actors/id/<int:actor_id>')
def get_actor(actor_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM actors WHERE id = %s", [actor_id])
    data = cur.fetchall()
    cur.close()
    newData = list()
    for actor in data:
        actorDict = OrderedDict()
        for i in range(len(actorStructure)):
            actorDict[actorStructure[i]] = actor[i]
        newData.append(actorDict)
    return jsonify(actorDict)


@app.route('/genres')
def get_genres():
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT genre FROM genre ORDER BY genre ASC")
    data = cur.fetchall()
    cur.close()
    dataClean = list()
    for dataGenre in data:
        dataClean.append(dataGenre[0])
    return jsonify(dataClean)


@app.route('/movies/genre/<string:genre>')
def get_movie_by_genre(genre):
    timeStart = time()

    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT movies.* FROM movies JOIN moviesGenres ON movies.id = moviesGenres.movie_id JOIN genre ON moviesGenres.genre_id = genre.id WHERE genre.genre = %s ORDER BY movies.score DESC", [genre])
    data = cur.fetchall()
    cur.close()
    newData = makeADict(movieStructure, data)
    cur.close()
    timeEnd = time()
    print(f"Tiempo de ejecución: {timeEnd - timeStart}")

    return jsonify(newData)


@app.route('/movies/search/<string:query>')
@app.route('/movies/search/<string:query>/<int:page>')
def search_movies(query: str, page: int = None):
    timeStart = time()

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
    newData = makeADict(movieStructure, data)
    cur.close()
    timeEnd = time()
    print(f"Tiempo de ejecución: {timeEnd - timeStart}")

    return jsonify(newData)


@app.route('/actors/search/<string:query>')
@app.route('/actors/search/<string:query>/<int:page>')
def search_actors(query: str, page: int = None):
    timeStart = time()

    cur = mysql.connection.cursor()
    if page:
        offset = (page - 1) * 10
        cur.execute(
            "SELECT * FROM actors WHERE names LIKE %s ORDER BY names ASC LIMIT 10 OFFSET %s", [f"%{query}%", offset])
    else:
        cur.execute(
            "SELECT * FROM actors WHERE names LIKE %s ORDER BY names ASC LIMIT 10", [f"%{query}%"])
    data = cur.fetchall()
    cur.close()
    newData = makeADict(actorStructure, data)
    return jsonify(newData)


if __name__ == '__main__':
    app.run(debug=True)
