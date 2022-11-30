#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, g, render_template, request, redirect, url_for
import numpy as np
import sqlite3
import pickle
import random
import pandas as pd
import io
import base64
import os

from recommendation import *

DEVELOPMENT_ENV  = True

app = Flask(__name__)

app_data = {
    "name":         "Steam Game Recommendation Application",
    "description":  "A basic Flask app",
    "html_title":   "CPSC 537 Final Project",
    "project_name": "CPSC 537 Steam Game Recommendation App",
}

UPLOAD_FOLDER = os.path.join('../static/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_user_db():
    # Check whether there is a database called user_db in the g attribute of the app
    if 'user_db' not in g:
        #  If not, then connect to that database, ensuring that the connection is an attribute of g
        g.user_db = sqlite3.connect("user_db.sqlite")

    if g.user_db is not None:
        cursor = g.user_db.cursor()
        # Check whether a table called user exists in user_db, and create it if not
        sql_create_user_table = """ CREATE TABLE IF NOT EXISTS user (
                                    id integer,
                                    name text,
                                    game_entered text,
                                    recommendation text
                                ); """
        cursor.execute(sql_create_user_table)
    # Return the connection
    return g.user_db

def insert_user_info(request):
    # open the connection
    g.user_db = get_user_db()
    cursor = g.user_db.cursor()
    # Extract user_name and game list from request
    name = request.form["name"]
    if name == "":
        name = "Anonymous"
    name = name.replace("'", "''")

    game_entered = request.form["game_entered"]
    game_entered = game_entered.replace("'", "''")

    recommendation = get_recommendation(game_user_likes=game_entered, num=request.form.get('num', type=int))

    # get nrow and assign unique id
    n_row = cursor.execute('select * from user;')
    nrow = len(n_row.fetchall()) + 1

    # add a new row to user database
    cursor.execute("INSERT INTO user (id, name, game_entered, recommendation) VALUES (?,  ?, ?, ?)",
    (nrow, name, game_entered, recommendation))
    # Save the change
    g.user_db.commit()
    # close the connection
    g.user_db.close()

def get_user_info():
    # open the connection
    g.user_db = get_user_db()
    # Get a collection of all user input from the user_db
    messages = pd.read_sql_query("SELECT * FROM user", g.user_db)
    # close the connection
    g.user_db.close()
    return messages

def generate_preview_info():
    # open the connection
    g.user_db = get_user_db()
    # get id number of the user
    id = int(request.form['user_id'])
    
    # Get a collection of all user input from the user_db
    messages = pd.read_sql_query("SELECT * FROM user where id = '{id}'".format(id = id), g.user_db)
    # close the connection
    g.user_db.close()

    str_r = messages.get('recommendation')[0]
    recommendation = list(str_r.split('/'))
    return messages, recommendation

@app.route('/')
def index():
    return render_template('index.html', app_data=app_data)


@app.route('/getuserinput', methods=['POST', 'GET'])
def getuserinput():
    if request.method == 'GET':
        return render_template('getuserinput.html', app_data=app_data)
    else: # if request.method == 'POST'
        try:
            insert_user_info(request)
            return render_template('thanks.html', app_data=app_data)
        except:
            return render_template('error.html', app_data=app_data)
            

@app.route('/Resultssummary', methods=['POST', 'GET'])
def Resultssummary():
    if request.method == 'GET':
        try:
            messages = get_user_info()
            return render_template('Resultssummary.html', messages = messages, app_data=app_data)
        except:
            return render_template('Resultssummary.html', app_data=app_data)
    else: # if request.method == 'POST'
        try:
            messages, games = generate_preview_info()
            return render_template('preview.html', app_data=app_data, messages = messages, games = games)
        except:
            return render_template('preview.html', app_data=app_data)

@app.route('/contact')
def contact():
    return render_template('contact.html', app_data=app_data)

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response

if __name__ == '__main__':
    app.run(debug=DEVELOPMENT_ENV)