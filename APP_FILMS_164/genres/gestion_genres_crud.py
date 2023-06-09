"""Gestion des "routes" FLASK et des données pour les genres.
Fichier : gestion_genres_crud.py
Auteur : OM 2021.03.16
"""
from pathlib import Path

from flask import redirect
from flask import request
from flask import session
from flask import url_for

from APP_FILMS_164 import app
from APP_FILMS_164.database.database_tools import DBconnection
from APP_FILMS_164.erreurs.exceptions import *
from APP_FILMS_164.genres.gestion_genres_wtf_forms import AjouterUtilisateur
from APP_FILMS_164.genres.gestion_genres_wtf_forms import FormWTFDeleteGenre
from APP_FILMS_164.genres.gestion_genres_wtf_forms import FormWTFUpdateGenre

"""
    Auteur : OM 2021.03.16
    Définition d'une "route" /genres_afficher
    
    Test : ex : http://127.0.0.1:5575/genres_afficher
    
    Paramètres : order_by : ASC : Ascendant, DESC : Descendant
                id_user_sel = 0 >> tous les genres.
                id_user_sel = "n" affiche le genre dont l'id est "n"
"""


@app.route("/genres_afficher/<string:order_by>/<int:id_user_sel>", methods=['GET', 'POST'])
def genres_afficher(order_by, id_user_sel):
    if request.method == "GET":
        try:
            with DBconnection() as mc_afficher:
                if order_by == "ASC" and id_user_sel == 0:
                    strsql_genres_afficher = """SELECT id_utilisateur, nom_utilisateur, prenom_utilisateur FROM t_utilisateurs ORDER BY id_utilisateur ASC"""
                    mc_afficher.execute(strsql_genres_afficher)
                elif order_by == "ASC":
                    # C'EST LA QUE VOUS ALLEZ DEVOIR PLACER VOTRE PROPRE LOGIQUE MySql
                    # la commande MySql classique est "SELECT * FROM t_utilisateurs"
                    # Pour "lever"(raise) une erreur s'il y a des erreurs sur les noms d'attributs dans la table
                    # donc, je précise les champs à afficher
                    # Constitution d'un dictionnaire pour associer l'id du genre sélectionné avec un nom de variable
                    valeur_id_user_selected_dictionnaire = {"value_id_user_selected": id_user_sel}
                    strsql_genres_afficher = """SELECT id_utilisateur, nom_utilisateur, prenom_utilisateur FROM t_utilisateurs WHERE id_utilisateur = %(value_id_user_selected)s"""

                    mc_afficher.execute(strsql_genres_afficher, valeur_id_user_selected_dictionnaire)
                else:
                    strsql_genres_afficher = """SELECT id_utilisateur, nom_utilisateur, prenom_utilisateur FROM t_utilisateurs ORDER BY id_utilisateur DESC"""

                    mc_afficher.execute(strsql_genres_afficher)

                data_genres = mc_afficher.fetchall()

                print("data_genres ", data_genres, " Type : ", type(data_genres))

                # Différencier les messages si la table est vide.
                if not data_genres and id_user_sel == 0:
                    flash("""La table "t_utilisateurs" est vide. !!""", "warning")
                elif not data_genres and id_user_sel > 0:
                    # Si l'utilisateur change l'id_utilisateur dans l'URL et que le genre n'existe pas,
                    flash(f"Le genre demandé n'existe pas !!", "warning")
                else:
                    # Dans tous les autres cas, c'est que la table "utilisateur" est vide.
                    # OM 2020.04.09 La ligne ci-dessous permet de donner un sentiment rassurant aux utilisateurs.
                    flash(f"Données textes affichés !!", "success")

        except Exception as Exception_genres_afficher:
            raise ExceptionGenresAfficher(f"fichier : {Path(__file__).name}  ;  "
                                          f"{genres_afficher.__name__} ; "
                                          f"{Exception_genres_afficher}")

    # Envoie la page "HTML" au serveur.
    return render_template("genres/genres_afficher.html", data=data_genres)


"""
    Auteur : OM 2021.03.22
    Définition d'une "route" /genres_ajouter
    
    Test : ex : http://127.0.0.1:5575/genres_ajouter
    
    Paramètres : sans
    
    But : Ajouter un genre pour un film
    
    Remarque :  Dans le champ "name_genre_html" du formulaire "genres/genres_ajouter.html",
                le contrôle de la saisie s'effectue ici en Python.
                On transforme la saisie en minuscules.
                On ne doit pas accepter des valeurs vides, des valeurs avec des chiffres,
                des valeurs avec des caractères qui ne sont pas des lettres.
                Pour comprendre [A-Za-zÀ-ÖØ-öø-ÿ] il faut se reporter à la table ASCII https://www.ascii-code.com/
                Accepte le trait d'union ou l'apostrophe, et l'espace entre deux mots, mais pas plus d'une occurence.
"""


@app.route("/genres_ajouter", methods=['GET', 'POST'])
def genres_ajouter_wtf():
    form = AjouterUtilisateur()
    if request.method == "POST":
        try:
            if form.validate_on_submit():
                nom_user_wtf = form.nom_user_wtf.data
                nom_user = nom_user_wtf.lower()
                prenom_user_wtf = form.prenom_user_wtf.data
                prenom_user = prenom_user_wtf.lower()

                valeurs_insertion_dictionnaire = {"value_nom_utilisateur": nom_user,
                                                  "value_prenom_utilisateur": prenom_user
                                                  }
                print("valeurs_insertion_dictionnaire ", valeurs_insertion_dictionnaire)

                strsql_inserutilisateur = """INSERT INTO t_utilisateurs (id_utilisateur,nom_utilisateur,prenom_utilisateur) VALUES (NULL,%(value_nom_utilisateur)s,%(value_prenom_utilisateur)s) """
                with DBconnection() as mconn_bd:
                    mconn_bd.execute(strsql_inserutilisateur, valeurs_insertion_dictionnaire)

                flash(f"Données insérées !!", "success")
                print(f"Données insérées !!")

                # Pour afficher et constater l'insertion de la valeur, on affiche en ordre inverse. (DESC)
                return redirect(url_for('genres_afficher', order_by='DESC', id_user_sel=0))

        except Exception as Exception_genres_ajouter_wtf:
            raise ExceptionGenresAjouterWtf(f"fichier : {Path(__file__).name}  ;  "
                                            f"{genres_ajouter_wtf.__name__} ; "
                                            f"{Exception_genres_ajouter_wtf}")

    return render_template("genres/image_ajouter_wtf.html", form=form)


"""
    Auteur : OM 2021.03.29
    Définition d'une "route" /genre_update
    
    Test : ex cliquer sur le menu "genres" puis cliquer sur le bouton "EDIT" d'un "genre"
    
    Paramètres : sans
    
    But : Editer(update) un genre qui a été sélectionné dans le formulaire "genres_afficher.html"
    
    Remarque :  Dans le champ "nom_user_update_wtf" du formulaire "genres/image_update_wtf.html",
                le contrôle de la saisie s'effectue ici en Python.
                On transforme la saisie en minuscules.
                On ne doit pas accepter des valeurs vides, des valeurs avec des chiffres,
                des valeurs avec des caractères qui ne sont pas des lettres.
                Pour comprendre [A-Za-zÀ-ÖØ-öø-ÿ] il faut se reporter à la table ASCII https://www.ascii-code.com/
                Accepte le trait d'union ou l'apostrophe, et l'espace entre deux mots, mais pas plus d'une occurence.
"""


@app.route("/genre_update", methods=['GET', 'POST'])
def genre_update_wtf():
    # L'utilisateur vient de cliquer sur le bouton "EDIT". Récupère la valeur de "id_utilisateur"
    id_user_update = request.values['id_user_btn_edit_html']

    # Objet formulaire pour l'UPDATE
    form_update = FormWTFUpdateGenre()
    try:
        print(" on submit ", form_update.validate_on_submit())
        if form_update.validate_on_submit():
            # Récupèrer la valeur du champ depuis "image_update_wtf.html" après avoir cliqué sur "SUBMIT".
            # Puis la convertir en lettres minuscules.
            name_genre_update = form_update.nom_user_update_wtf.data
            name_genre_update = name_genre_update.lower()
            date_genre_essai = form_update.date_genre_wtf_essai.data

            valeur_update_dictionnaire = {"value_id_user": id_user_update,
                                          "value_name_genre": name_genre_update,
                                          "value_date_genre_essai": date_genre_essai
                                          }
            print("valeur_update_dictionnaire ", valeur_update_dictionnaire)

            str_sql_update_intitulegenre = """UPDATE t_utilisateurs SET nom_utilisateur = %(value_name_genre)s, 
            prenom_utilisateur = %(value_date_genre_essai)s WHERE id_utilisateur = %(value_id_user)s """
            with DBconnection() as mconn_bd:
                mconn_bd.execute(str_sql_update_intitulegenre, valeur_update_dictionnaire)

            flash(f"Donnée mise à jour !!", "success")
            print(f"Donnée mise à jour !!")

            # afficher et constater que la donnée est mise à jour.
            # Affiche seulement la valeur modifiée, "ASC" et l'"id_user_update"
            return redirect(url_for('genres_afficher', order_by="ASC", id_user_sel=id_user_update))
        elif request.method == "GET":
            # Opération sur la BD pour récupérer "id_utilisateur" et "nom_utilisateur" de la "utilisateur"
            str_sql_id_user = "SELECT id_utilisateur, nom_utilisateur, prenom_utilisateur FROM t_utilisateurs " \
                               "WHERE id_utilisateur = %(value_id_user)s"
            valeur_select_dictionnaire = {"value_id_user": id_user_update}
            with DBconnection() as mybd_conn:
                mybd_conn.execute(str_sql_id_user, valeur_select_dictionnaire)
            # Une seule valeur est suffisante "fetchone()", vu qu'il n'y a qu'un seul champ "nom genre" pour l'UPDATE
            data_nom_genre = mybd_conn.fetchone()
            print("data_nom_genre ", data_nom_genre, " type ", type(data_nom_genre), " genre ",
                  data_nom_genre["nom_utilisateur"])

            # Afficher la valeur sélectionnée dans les champs du formulaire "image_update_wtf.html"
            form_update.nom_user_update_wtf.data = data_nom_genre["nom_utilisateur"]
            form_update.date_genre_wtf_essai.data = data_nom_genre["prenom_utilisateur"]

    except Exception as Exception_genre_update_wtf:
        raise ExceptionGenreUpdateWtf(f"fichier : {Path(__file__).name}  ;  "
                                      f"{genre_update_wtf.__name__} ; "
                                      f"{Exception_genre_update_wtf}")

    return render_template("genres/image_update_wtf.html", form_update=form_update)


"""
    Auteur : OM 2021.04.08
    Définition d'une "route" /genre_delete
    
    Test : ex. cliquer sur le menu "genres" puis cliquer sur le bouton "DELETE" d'un "genre"
    
    Paramètres : sans
    
    But : Effacer(delete) un genre qui a été sélectionné dans le formulaire "genres_afficher.html"
    
    Remarque :  Dans le champ "nom_genre_delete_wtf" du formulaire "genres/image_delete_wtf.html",
                le contrôle de la saisie est désactivée. On doit simplement cliquer sur "DELETE"
"""


@app.route("/genre_delete", methods=['GET', 'POST'])
def genre_delete_wtf():
    data_films_attribue_genre_delete = None
    btn_submit_del = None
    # L'utilisateur vient de cliquer sur le bouton "DELETE". Récupère la valeur de "id_utilisateur"
    id_user_delete = request.values['id_user_btn_delete_html']

    # Objet formulaire pour effacer le genre sélectionné.
    form_delete = FormWTFDeleteGenre()
    try:
        print(" on submit ", form_delete.validate_on_submit())
        if request.method == "POST" and form_delete.validate_on_submit():

            if form_delete.submit_btn_annuler.data:
                return redirect(url_for("genres_afficher", order_by="ASC", id_user_sel=0))

            if form_delete.submit_btn_conf_del.data:
                # Récupère les données afin d'afficher à nouveau
                # le formulaire "genres/image_delete_wtf.html" lorsque le bouton "Etes-vous sur d'effacer ?" est cliqué.
                data_films_attribue_genre_delete = session['data_films_attribue_genre_delete']
                print("data_films_attribue_genre_delete ", data_films_attribue_genre_delete)

                flash(f"Effacer le genre de façon définitive de la BD !!!", "danger")
                # L'utilisateur vient de cliquer sur le bouton de confirmation pour effacer...
                # On affiche le bouton "Effacer genre" qui va irrémédiablement EFFACER le genre
                btn_submit_del = True

            if form_delete.submit_btn_del.data:
                valeur_delete_dictionnaire = {"value_id_user": id_user_delete}
                print("valeur_delete_dictionnaire ", valeur_delete_dictionnaire)

                str_sql_delete_films_genre = """DELETE FROM utilisateur_film WHERE fk_genre = %(value_id_user)s"""
                str_sql_delete_idgenre = """DELETE FROM t_utilisateurs WHERE id_utilisateur = %(value_id_user)s"""
                # Manière brutale d'effacer d'abord la "fk_genre", même si elle n'existe pas dans la "utilisateur_film"
                # Ensuite on peut effacer le genre vu qu'il n'est plus "lié" (INNODB) dans la "utilisateur_film"
                with DBconnection() as mconn_bd:
                    mconn_bd.execute(str_sql_delete_films_genre, valeur_delete_dictionnaire)
                    mconn_bd.execute(str_sql_delete_idgenre, valeur_delete_dictionnaire)

                flash(f"Genre définitivement effacé !!", "success")
                print(f"Genre définitivement effacé !!")

                # afficher les données
                return redirect(url_for('genres_afficher', order_by="ASC", id_user_sel=0))

        if request.method == "GET":
            valeur_select_dictionnaire = {"value_id_user": id_user_delete}
            print(id_user_delete, type(id_user_delete))

            # Requête qui affiche tous les films_genres qui ont le genre que l'utilisateur veut effacer
            str_sql_genres_films_delete = """SELECT id_user_film, nom_film, id_utilisateur, nom_utilisateur FROM utilisateur_film 
                                            INNER JOIN t_film ON utilisateur_film.fk_film = t_film.id_film
                                            INNER JOIN t_utilisateurs ON utilisateur_film.fk_genre = t_utilisateurs.id_utilisateur
                                            WHERE fk_genre = %(value_id_user)s"""

            with DBconnection() as mydb_conn:
                mydb_conn.execute(str_sql_genres_films_delete, valeur_select_dictionnaire)
                data_films_attribue_genre_delete = mydb_conn.fetchall()
                print("data_films_attribue_genre_delete...", data_films_attribue_genre_delete)

                # Nécessaire pour mémoriser les données afin d'afficher à nouveau
                # le formulaire "genres/image_delete_wtf.html" lorsque le bouton "Etes-vous sur d'effacer ?" est cliqué.
                session['data_films_attribue_genre_delete'] = data_films_attribue_genre_delete

                # Opération sur la BD pour récupérer "id_utilisateur" et "nom_utilisateur" de la "utilisateur"
                str_sql_id_user = "SELECT id_utilisateur, nom_utilisateur FROM t_utilisateurs WHERE id_utilisateur = %(value_id_user)s"

                mydb_conn.execute(str_sql_id_user, valeur_select_dictionnaire)
                # Une seule valeur est suffisante "fetchone()",
                # vu qu'il n'y a qu'un seul champ "nom genre" pour l'action DELETE
                data_nom_genre = mydb_conn.fetchone()
                print("data_nom_genre ", data_nom_genre, " type ", type(data_nom_genre), " genre ",
                      data_nom_genre["nom_utilisateur"])

            # Afficher la valeur sélectionnée dans le champ du formulaire "image_delete_wtf.html"
            form_delete.nom_genre_delete_wtf.data = data_nom_genre["nom_utilisateur"]

            # Le bouton pour l'action "DELETE" dans le form. "image_delete_wtf.html" est caché.
            btn_submit_del = False

    except Exception as Exception_genre_delete_wtf:
        raise ExceptionGenreDeleteWtf(f"fichier : {Path(__file__).name}  ;  "
                                      f"{genre_delete_wtf.__name__} ; "
                                      f"{Exception_genre_delete_wtf}")

    return render_template("genres/image_delete_wtf.html",
                           form_delete=form_delete,
                           btn_submit_del=btn_submit_del,
                           data_films_associes=data_films_attribue_genre_delete)
