# YALE CPSC 537 Final Project - Steam Game Recommendation App

## Team members
- Lang Ding (ld698)
- Yuxuan Cheng (yc757)
- Shurui Wang (sw2349)


## How to run this app on your computer from command line
 At the command prompt or terminal, navigate to your projects directory
- Mac: $ export FLASK_ENV=development; flask run
- Windows: set FLASK_ENV=development; flask run

Site will be available at: http://localhost:5000

Note:

- Please make sure you have installed the required versions of all python packages needed in [requirements.txt](https://github.com/JadenWSR/SteamProject/blob/main/requirements.txt) before you run the app. For both Mac and Windows: `pip install -r requirements.txt`
- Please make sure your Python version is above **3.10**. Otherwise, the match-case function in database.py will throw an error and would lead to the whole app failing to work.

## Description

There are a large number of games available on Steam. To find a new game that matches their interest, people may waste plenty of time searching on the Steam store and may have a hard time finding the game that they are potentially interested in. To solve this problem, our team decided to build a self-contained local web application that provides the user with some game recommendations and game information previews efficiently.  

We have created a cosine-similarity-based model on our local Python flask web application, using data cleaning and processing techniques and database management skills. Our web application will recommend Steam games to the user based on their input Steam game and customized searching criteria. Recommendations will be generated using our built-in model and the user will be able to review all information listed on Steam for our recommended games, or be redirected to the Steam store if they wish to purchase the game we recommended. All the searching and recommending procedures can be done locally by utilizing our Steam game database, without searching online via the Steam store. Also, people are able to keep track of their previous recommendation records on our Web application, as they are stored locally in our User database.

## Database Schema Design

![schema_design.jpg](/static/schema_design.jpg)
