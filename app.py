#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, g, render_template, request, redirect, url_for, make_response, jsonify
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
app.config['JSON_SORT_KEYS'] = False

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
                                    id integer PRIMARY KEY,
                                    name text,
                                    game_entered text,
                                    recommendation text
                                ); """
        cursor.execute(sql_create_user_table)
    # Return the connection
    return g.user_db

def filter_data(request):
    tags = request.form['tag']
    genres = request.form['genre']
    categories = request.form['category']
    t = tuple()
    if all(x == "" for x in (tags,genres, categories)):
        # No filter condition input
        cmd = """select * from Steam_game"""
    else:
        # at least one filter condition is not empty
        cmd = """select * from Steam_game where"""
        if tags != "":
            if cmd[len(cmd)-5:len(cmd)] != "where":
                cmd += " and"
            tags = list(map(str.strip, tags.split(';')))
            for tag in tags:
                cmd += " tags like ? or"
                t += ('%'+ str(tag) + '%',)
            cmd = cmd[:len(cmd) - 3]
        if genres != "":
            if cmd[len(cmd)-5:len(cmd)] != "where":
                cmd += " and"
            genres = list(map(str.strip, genres.split(';')))
            for genre in genres:
                cmd += " genre like ? or"
                t += ('%'+ str(genre) + '%',)
            cmd = cmd[:len(cmd) - 3]
        if categories != "":
            if cmd[len(cmd)-5:len(cmd)] != "where":
                cmd += " and"
            categories = list(map(str.strip, categories.split(';')))
            for category in categories:
                cmd += " categories like ? or"
                t += ('%'+ str(category) + '%',)
            cmd = cmd[:len(cmd) - 3]
    return cmd, t

def insert_user_info(request):
    # open the connection
    g.user_db = get_user_db()
    cursor = g.user_db.cursor()
    # Extract user_name and game list from request
    name = request.form["name"]
    if name == "":
        name = "Anonymous User"
    name = name.replace("'", "''")

    game_entered = request.form["game_entered"]
    game_entered = game_entered.replace("'", "''")
    cmd, t = filter_data(request)

    recommendation = get_recommendation_by_filter(game_user_likes = game_entered, num = request.form.get('num', type=int), t = t, query = cmd)
    # get nrow and assign unique id
    n_row = cursor.execute('select * from user;')
    nrow = len(n_row.fetchall()) + 1

    # add a new row to user database
    cursor.execute("INSERT INTO user (id, name, game_entered, recommendation) VALUES (?, ?, ?, ?)",
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
    #id = int(request.form['user_id'])
    id = int(request.args.get('user_id'))
    
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
        html = render_template('getuserinput.html', app_data=app_data)
        response = make_response(html)
        return response
        # return render_template('getuserinput.html', app_data=app_data)
    else: # if request.method == 'POST'
        try:
            insert_user_info(request)
            return render_template('thanks.html', app_data=app_data)
        except:
            return render_template('error.html', app_data=app_data)

@app.route('/searchresults', methods=['GET'])           
def handle_search():
    author = request.args.get('author')
    if (author is None) or (author.strip() == ''):
        response = make_response('')
        return response

    books = search(author)  # Exception handling omitted

    html = '''
    <style>
    #myTable {
        border-collapse: collapse;
        width: 50%;
        border: 1px solid #ddd;
        font-size: 18px;
    }

    #myTable th, #myTable td {
        text-align: left;
        padding: 12px;
    }

    #myTable tr {
        border-bottom: 1px solid #ddd;
    }

    #myTable tr.header, #myTable tr:hover {
        background-color: #f1f1f1;
    }

    </style>

    <table id="myTable">
    <thead>
        <tr class="header">
            <th>Game</th>
        </tr>
    </thead>
    <tbody>
    '''

    pattern = '''
    <tr game="%s">
        <td>%s</td>   
    </tr>
    '''
    for book in books[0:5]:
        html += pattern % (book,book)

    html += '''
    </tbody>
    </table>
    '''

    response = make_response(html)
    return response

@app.route('/Resultssummary', methods=['POST', 'GET'])
def Resultssummary():
    if request.method == 'GET':
        try:
            messages = get_user_info()
            return render_template('Resultssummary.html', messages = messages, app_data=app_data)
        except:
            return render_template('Resultssummary.html', app_data=app_data, error = True)
    else: # if request.method == 'POST'
        try:
            return redirect('/preview')
        except:
            return render_template('error_preview.html', app_data=app_data)

@app.route('/preview', methods=['POST', 'GET'])
def preview():
    try:
        id = int(request.args.get('user_id'))
        messages, games = generate_preview_info()
        return render_template('preview.html', app_data=app_data, messages = messages, games = games, id = id)
    except:
        return render_template('error_preview.html', app_data=app_data)

@app.route('/previewSingleGame')
def previewSingleGame():
    try:
        id = int(request.args.get('user_id'))
        select =  request.args.get("game_selected")
        dict = game_api(select).get_json()

        return render_template('previewSingleGame.html', app_data=app_data, dict = dict, select = select, id = id)
    except:
        return render_template('error_preview.html', app_data=app_data)


# api to get info for a specific game
@app.route("/info/<string:name>")
def game_api(name):
    name = name.strip()
    info = full_df[full_df.Name == name]
    # join developer table to get developer name
    # open games db connection
    cli_game = CLI()

    devs = ''
    dev_id = info['developer_id'].item()
    dev_id = list(eval(dev_id))
    dev_id = [int(i) for i in dev_id if i]
    for id in dev_id:
            name = ''
            if cli_game._api.get_dev_name(id):
                name = cli_game._api.get_dev_name(id)[0][0]
            devs += name
            devs += ' '
    info["Developer"] = devs

    return jsonify({
        "Steam appid": info['appid'].item(),
        "Name": info['Name'].item(),
        'Release Date': info['release_date'].item(),
        'Tags': info['Tags'].item(),
        'Categories': info['Categories'].item(),
        'Developer': info['Developer'].item()})


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