import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from heapq import nlargest

df = pd.read_csv(r"./Data/steam_games.csv", header=0, sep=";", low_memory=False)
# print(df.head)

features = ['Developer', 'Genre', 'Categories', 'Tags']
for feature in features:
    df[feature] = df[feature].fillna('')

def combined_features(row):
    com = ''
    for feature in features:
        com += row[feature] + ' '
    return com

df["combined_features"] = df.apply(combined_features, axis =1)

cv = CountVectorizer()
count_matrix = cv.fit_transform(df["combined_features"])



def get_index_from_title(title):
    return df[df.Name == title].index.item()

def get_title_from_index(index):
        return df[df.index == index]["Name"].values[0]

def get_recommendation(game_user_likes = "Crysis 3", num = 5):
    game_index = get_index_from_title(game_user_likes)

    cosine_sim = cosine_similarity(count_matrix[game_index],count_matrix)[0]

    similar_games = list(enumerate(cosine_sim))
    # sorted_similar_movies = sorted(similar_movies, key=lambda x:x[1], reverse=True)
    sorted_similar_games = nlargest(num + 1, similar_games, key=lambda x:x[1])[1::]

    recom_list = []
    for game in sorted_similar_games:
        recom_list.append(get_title_from_index(game[0]))
    
    str = " / ".join(recom_list)
    return str

def search(name):
    # names = df[df.Name == name]["Name"]
    filter = df.Name.str.contains(name, case=False)
    names = df[filter]["Name"]
    if not names.empty:
        return names.values
    else:
        return ['None']

if __name__ == '__main__':
    print(get_recommendation("Sniper Elite 5", num = 2))