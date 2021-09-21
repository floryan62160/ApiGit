"""
Cette API sera une application Python en REST et devra respecter le CRUD pour la base de donnée sakila.
Nous travaillons dans un premier temps sur les articles bières sans foreign key.

On doit donc faire plusieurs fonctions : Get / Get_byId / Update / Create and Delete.
"""

# Import de flask et de mysql
from flask import Flask, abort, request
from flask.helpers import make_response, url_for
from flask.json import jsonify
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)

# Appel de mysql pour utiliser notre base de donnée beer
mysql = MySQL(app)
# Configuration à la connection mysql
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
# Ici on informe qu'on se connecte a la base "beer" de mysql
app.config['MYSQL_DB'] = 'sakila'


# Lancer mon application
if __name__ == "__main__":
    app.run(debug=True)



# Page d'accueil : bienvenue sur l'API
@app.route('/')
def index():
    return "Bienvenue sur l'API de la base de donnée sakila."


# ==========================================================ACTOR=======================================================

# ==========================================================READ-ACTOR==================================================

# Preimère route pour récupèrer toutes les bières.
@app.route('/actors',methods=['GET'])
def get_actors():
    # On verifie qu'il n'y aucun problème dans notre requète
    try :
        # On établit la connection avec la base de données
        cur = mysql.connection.cursor()
        # On execute la requète souhaitée
        cur.execute("SELECT * FROM actor")
        # On récupère toutes les lignes de la requete
        response = cur.fetchall()
        # On peut fermer la connection a mysql
        cur.close()

        # On va stocker l'ensemble de nos bières dans une nouvelle liste
        actors = []
        for actor in response:
            # On transforme la bière, dans response la bière est un tuple
            actor = make_actor(actor)
            # On ajoute la nouvelle bière a notre liste total
            actors.append(actor)
        # On affiche l'ensemble des bières de la liste
        return jsonify([make_public_actor(actor) for actor in actors])
    # On relève un problème et on return une erreur 404
    except Exception as e:
        print(e)
        abort(404)




# Route pour récuperer une bière de la liste precise
@app.route('/actors/<int:actor_id>', methods = ['GET'])
def get_actor_by_id(actor_id):
    # On verifie qu'il n'y aucun problème dans notre requète
    try :
        # On se connecte a la base mysql
        cur = mysql.connection.cursor()
        # On execute la requète souhaitée, ici on récupère l'id de l'article en question
        cur.execute("SELECT * FROM actor WHERE actor_id= %s" ,(str(actor_id),))
        # Nous avons une seule ligne, on recupère donc une seule ligne
        reponse = cur.fetchone()
        # On peut fermer la connection a la base mysql
        cur.close()
        # On transforme la réponse tuple en une liste modifiable 
        reponse = make_actor(reponse)
        # On affiche cette bière a l'utilisateur
        return jsonify(make_public_actor(reponse))
    # On relève un problème, on retourne une erreur 404
    except Exception as e:
        print(e)
        abort(404)




# Fonction qui transforme la bière tuple en une bière liste 
def make_actor(actor):
    list_actor = list(actor)
    # On créer le nouvel objet qui prendra les même arguments que la bière mais sous forme de liste
    new_actor = {}
    new_actor['actor_id'] = int(list_actor[0])
    new_actor['first_name'] = str(list_actor[1])
    new_actor['last_name'] = str(list_actor[2])
    new_actor['last_update'] = str(list_actor[3])

    # On retourne notre nouvel article avec les mêmes arguments mais sous forme de liste modifiable
    return new_actor



# Fonction pour créer une URL de façon dynamique à partir d'une tache
def make_public_actor(actor):
    # On créer un nouvel objet dans lequel l'id n'apparaitra pas
    public_actor = {}
    for argument in actor:

        # Si l'argument est l'id de l'article
        if argument == "actor_id":
            # On change cette argument en un URL vers l'adresse de l'article 
            public_actor['url'] = url_for('get_actor_by_id', actor_id = actor["actor_id"], _external = True)

        # Les autres arguments restent identiques
        else :
            public_actor[argument] = actor[argument]
    # On retourne cette nouvelle bière
    return public_actor



# ==========================================================CREATE-ACTOR=======================================================


# Fonction qui créer une bière :
@app.route('/actors',methods = ['POST'])
def create_actor(): 
    # Verification que les arguments indispensables soient recensés
    if not request.json:
        abort(400)
    if not "first_name" in request.json:
        abort(400)
    if not "last_name" in request.json:
        abort(400)

    # On verifie qu'il n'y a pas d'erreur dans notre requète
    try :
        # On recupère les informations souhaitées
        first_name = request.json.get("first_name")
        last_name = request.json.get("last_name")

        # Créer et envoyer à la Bdd
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO actor(first_name,last_name,last_update) VALUES (%s,%s,current_timestamp())",(first_name,last_name))
        mysql.connection.commit()
        # On referme la connection à la base
        cur.close()
        return jsonify({'is':True})
    except Exception as e:
        print(e)
        return jsonify({'is': False})


# ==========================================================UPDATE-ACTOR=======================================================


# Route pour modifier une bière precise de ma liste
@app.route('/actors/<int:actor_id>', methods = ['PUT'])
def update_actor_by_id(actor_id):
    actor = get_actor_by_id(actor_id)
    # On verifie les erreurs possibles
    if not request.json:
        abort(400)
    if  "actor_id" in request.json and type(request.json["actor_id"]) is not int:
        abort(404)
    if "first_name" in request.json and type(request.json["first_name"]) is not str:
        abort(404)
    if "last_name" in request.json and type(request.json["last_name"]) != str:
        abort(404) 

    # On modifie la tache souhaitée
    try :
        # On recupère les informations données par l'utilisateur

        # On verifie si le nom d'article change
        first_name = request.json.get("first_name", actor.json.get("first_name"))
        last_name = request.json.get("last_name", actor.json.get("last_name"))

        # On se connecte a la base de donnée
        cur = mysql.connection.cursor()
        # On update l'article en question
        cur.execute("UPDATE actor SET first_name=%s,last_name=%s, last_update=current_timestamp() WHERE actor_id = %s",(str(first_name),str(last_name),actor_id))
        mysql.connection.commit()
        # On ferme la connection à la base de donnée
        cur.close()
        # On retourne l'article modifier 
        return get_actor_by_id(actor_id)
    except Exception as e:
        print(e)
        return jsonify({'is' : False})




# ==========================================================DELETE-ACTOR=======================================================

# Route pour supprimer une certaine tache
@app.route('/actors/<int:actor_id>', methods = ['DELETE'])
def delete_tctor_by_id(actor_id):
    # On récupère la tache a supprimer
    actor = get_actor_by_id(actor_id)
    # On va ici verifier que la suppression se passe bien
    try :
        # On se connecte à la base de donnée
        cur = mysql.connection.cursor()
        # On demande de supprimer l'aricle en question
        cur.execute("DELETE FROM actor WHERE actor_id = %s" ,(str(actor_id),))
        mysql.connection.commit()
        # On ferme la connection à la base de donnée
        cur.close()
        # On retourne l'article supprimer en cas de problème
        return actor
    except Exception as e:
        print(e)
        return jsonify({'is': False})






# ==========================================================FILM=======================================================

# ==========================================================READ-FILM================================================


# Preimère route pour récupèrer toutes les bières.
@app.route('/films',methods=['GET'])
def get_films():
    # On verifie qu'il n'y aucun problème dans notre requète
    try :
        # On établit la connection avec la base de données
        cur = mysql.connection.cursor()
        # On execute la requète souhaitée
        cur.execute("SELECT * FROM film")
        # On récupère toutes les lignes de la requete
        response = cur.fetchall()
        # On peut fermer la connection a mysql
        cur.close()

        # On va stocker l'ensemble de nos bières dans une nouvelle liste
        films = []
        for film in response:
            # On transforme la bière, dans response la bière est un tuple
            film = make_film(film)
            # On ajoute la nouvelle bière a notre liste total
            films.append(film)
        # On affiche l'ensemble des bières de la liste
        return jsonify([make_public_film(film) for film in films])
    # On relève un problème et on return une erreur 404
    except Exception as e:
        print(e)
        abort(404)




# Route pour récuperer une bière de la liste precise
@app.route('/films/<int:film_id>', methods = ['GET'])
def get_film_by_id(film_id):
    # On verifie qu'il n'y aucun problème dans notre requète
    try :
        # On se connecte a la base mysql
        cur = mysql.connection.cursor()
        # On execute la requète souhaitée, ici on récupère l'id de l'article en question
        cur.execute("SELECT * FROM film WHERE film_id= %s" ,(str(film_id),))
        # Nous avons une seule ligne, on recupère donc une seule ligne
        reponse = cur.fetchone()
        # On peut fermer la connection a la base mysql
        cur.close()
        # On transforme la réponse tuple en une liste modifiable 
        reponse = make_film(reponse)
        # On affiche cette bière a l'utilisateur
        return jsonify(make_public_film(reponse))
    # On relève un problème, on retourne une erreur 404
    except Exception as e:
        print(e)
        abort(404)




# Fonction qui transforme la bière tuple en une bière liste 
def make_film(film):
    list_film = list(film)
    # On créer le nouvel objet qui prendra les même arguments que la bière mais sous forme de liste
    new_film = {}
    new_film['film_id'] = int(list_film[0])
    new_film['title'] = str(list_film[1])

    if list_film[2] == None :
        new_film["description"] == None
    else :
        new_film['description'] = str(list_film[2])


    if list_film[3] == None:
        new_film['release_year'] == None
    else:
        new_film['release_year'] = int(list_film[3])

    new_film['language_id'] = int(list_film[4])
    new_film['rental_duration'] = int(list_film[6])
    new_film['rental_rate'] = float(list_film[7])

    if list_film[8] == None:
        new_film['length'] == None
    else:
        new_film['length'] = int(list_film[8])

    new_film['replacement_cost'] = float(list_film[9])
    if list_film[10] == None:
        new_film['length'] == None
    else:
        new_film['rating'] = str(list_film[10])

    if list_film[11] == None:
        new_film['special_features'] == None
    else :
        new_film['special_features'] = str(list_film[11])

    new_film['last_update'] = str(list_film[12])

    # On retourne notre nouvel article avec les mêmes arguments mais sous forme de liste modifiable
    return new_film



# Fonction pour créer une URL de façon dynamique à partir d'une tache
def make_public_film(film):
    # On créer un nouvel objet dans lequel l'id n'apparaitra pas
    public_film = {}
    for argument in film:

        # Si l'argument est l'id de l'article
        if argument == "film_id":
            # On change cette argument en un URL vers l'adresse de l'article 
            public_film['url'] = url_for('get_film_by_id', film_id = film["film_id"], _external = True)

        # Les autres arguments restent identiques
        else :
            public_film[argument] = film[argument]
    # On retourne cette nouvelle bière
    return public_film



# ==========================================================CREATE-FILM=======================================================


# Fonction qui créer une bière :
@app.route('/films',methods = ['POST'])
def create_film(): 
    # Verification que les arguments indispensables soient recensés
    if not request.json:
        abort(400)
    if not "rental_duration" in request.json:
        abort(400)
    if not "rental_rate" in request.json:
        abort(400)
    if not "replacement_cost" in request.json:
        abort(400)
    if not "title" in request.json:
        abort(400)
    if not "language_id" in request.json:
        abort(400)
    # On verifie qu'il n'y a pas d'erreur dans notre requète
    try :
        # On recupère les informations souhaitées
        title = request.json.get("title")
        description = request.json.get("description")
        release_year = request.json.get("release_year")
        language_id = request.json.get("language_id")
        rental_duration = request.json.get("rental_duration")
        rental_rate = request.json.get("rental_rate")
        length = request.json.get("length")
        replacement_cost = request.json.get("replacement_cost")
        rating = request.json.get("rating")
        special_features = request.json.get("special_features")

        print(release_year)
        # On verifie si le titrage est nul
        if description == "":
            description = None

        if length == None:
            length = 0

        if rating == "":
            rating = None

        if release_year == None:
            release_year = 0

        if special_features == "":
            special_features = None


        # Créer et envoyer à la Bdd
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO film(title,description,release_year,language_id,original_language_id,rental_duration,rental_rate,length,replacement_cost,rating,special_features,last_update) VALUES (%s,%s,%s,%s,Null,%s,%s,%s,%s,%s,%s,current_timestamp())", (title,description,str(release_year),str(language_id),str(rental_duration),str(rental_rate),str(length),str(replacement_cost),str(rating),str(special_features)))
        mysql.connection.commit()
        # On referme la connection à la base
        cur.close()
        return jsonify({'is':True})
    except Exception as e:
        print(e)
        return jsonify({'is': False})



# ==========================================================DELETE-FILM=======================================================

# Route pour supprimer une certaine tache
@app.route('/films/<int:film_id>', methods = ['DELETE'])
def delete_film_by_id(film_id):
    # On récupère la tache a supprimer
    film = get_film_by_id(film_id)
    # On va ici verifier que la suppression se passe bien
    try :
        # On se connecte à la base de donnée
        cur = mysql.connection.cursor()
        # On demande de supprimer l'aricle en question
        cur.execute("DELETE FROM film WHERE film_id = %s" ,(str(film_id),))
        mysql.connection.commit()
        # On ferme la connection à la base de donnée
        cur.close()
        # On retourne l'article supprimer en cas de problème
        return film
    except Exception as e:
        print(e)
        return jsonify({'is': False})


# ==========================================================UPDATE-FILM=======================================================