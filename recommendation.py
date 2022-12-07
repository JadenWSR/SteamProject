import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from heapq import nlargest
from dataBase import CLI

cli = CLI()
c = cli._api._connection.cursor()
c.execute(''' SELECT * FROM Steam_game''')
results = c.fetchall()
full_df = pd.DataFrame(results, columns = ['appid', 'Name', 'release_date', 'Genre', 'Tags', 'Categories', 'developer_id'])

def get_recommendation_by_filter(game_user_likes, num, t, query=''' SELECT * FROM Steam_game'''):
    cli = CLI()
    c = cli._api._connection.cursor()
    c.execute(query, t)
    results = c.fetchall()
    df = pd.DataFrame(results, columns = ['appid', 'Name', 'release_date', 'Genre', 'Tags', 'Categories', 'developer_id'])
    if df.Name.str.contains(game_user_likes, case=False).sum() == 0:
        # handle invalid searching filters
        df = full_df.copy()

    def add_developer_name(row):
        devs = ''
        dev_id = row['developer_id']
        dev_id = re.split(r'[(,)]',dev_id)
        dev_id = [int(i) for i in dev_id if i]
        for id in dev_id:
            name = ''
            if cli._api.get_dev_name(id):
                name = cli._api.get_dev_name(id)[0][0]
            devs += name
            devs += ' '
        return devs

    df["Developer"] = df.apply(add_developer_name, axis =1)

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
        return df[df.Name == title].index[0]

    def get_title_from_index(index):
        return df[df.index == index]["Name"].values[0]

    def get_recommendation(game_user_likes, num):
        game_index = get_index_from_title(game_user_likes)

        cosine_sim = cosine_similarity(count_matrix[game_index],count_matrix)[0]

        similar_games = list(enumerate(cosine_sim))
        
        sorted_similar_games = nlargest(num + 1, similar_games, key=lambda x:x[1])[1::]

        recom_list = []
        for game in sorted_similar_games:
            recom_list.append(get_title_from_index(game[0]))
        
        str = " / ".join(recom_list)
        return str


    return get_recommendation(game_user_likes, num)

def search(name):
    filter = full_df.Name.str.contains(name, case=False)
    names = full_df[filter]["Name"]
    if not names.empty:
        return names.values
    else:
        return ['None']
    

if __name__ == '__main__':
    # print(get_recommendation_by_filter(game_user_likes = "GridlessDB", num = 5, query = """select * from Steam_game where tags like ? or tags like ? and genre like ? or genre like ? and categories like ? or categories like ?""",
    # t = ('%action%','%casual%', '%action%','%casual%', '%single%', '%multi%')))
    # print(full_df[full_df.Name == 'GridlessDB']['appid'].item())
    # print(get_recommendation_by_filter('Ricochet', 5, tuple(), query=''' SELECT * FROM Steam_game'''))
    duplicate_in_student = full_df.duplicated(subset=['Name'])
    if duplicate_in_student.any():
        print(full_df.loc[~duplicate_in_student], end='\n\n')