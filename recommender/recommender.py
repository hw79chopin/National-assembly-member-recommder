import json
import pandas as pd
from random import shuffle
from collections import Counter
from gensim.models import Word2Vec, FastText, Doc2Vec
from sklearn.metrics.pairwise import cosine_similarity

class Recommend:
    def __init__(self, senators, model):
        self.senators_json = senators
        self.embedding_model = model

        word_dict = {}
        for vocab, vector in zip(self.embedding_model.wv.index2word, self.embedding_model.wv.vectors):
            word_dict[vocab] = vector
        self.word_dict = word_dict

    def search(self, user_input):
        temp_list = []
        for word in self.word_dict:
            if user_input in word:
                temp_list.append(word)
        return temp_list

    def similarWord(self, text):
        return self.embedding_model.most_similar(positive=[text], topn=30)

    def similar_senators(self, user_input, senators_json):
        # user_vector 만들기
        list_vector =[]
        for word in user_input:
            if word in self.word_dict.keys():
                list_vector.append(self.word_dict[word])
        user_vector = np.sum(list_vector, axis=0).tolist()
        
        # senator 찾기
        similarity = {}
        for item in senators_json:
            sim = cosine_similarity(np.array(user_vector).reshape(1,-1), np.array(senators_json[item]['vector']).reshape(1,-1))
            similarity['{} {}'.format(senators_json[item]['한글이름'], senators_json[item]['정당'])] = float(sim)
        
    # sort해서 {} [] 만들어주고 Top 5 뽑기
        similarity = {key: value for key, value in sorted(similarity.items(), key=lambda item: item[1], reverse=True)}
        rating = [key for key, value in sorted(similarity.items(), key=lambda item: item[1], reverse=True)]
        return rating[:5]

    def show_senators_bills_contents(self, senators_list, df_bills):
        dict_senator_bills = {}
        for senator in senators_list:
            senator_name = senator.split(" ", 1)[0]
            bills_id_bySenator = df_bills[df_bills['발의자'].str.contains(senator_name)].bill_id.values.tolist()

            list_temp_keyword_bills_ids = []
            for keyword in user_input:
                bills_id_byKeyword = df_bills.loc[bills_id_bySenator]['bill_id'].values.tolist()
                df_semi = df_bills.loc[bills_id_byKeyword]
                semi_result = df_semi[df_semi['법안명_법안내용'].str.contains(keyword)]['bill_id'].drop_duplicates().values.tolist()
                list_temp_keyword_bills_ids.extend(semi_result)
            list_temp_keyword_bills_ids = list(set(list_temp_keyword_bills_ids))
            shuffle(list_temp_keyword_bills_ids)
            list_bills_title = df_bills[df_bills['bill_id'].isin(list_temp_keyword_bills_ids[:3])]['법안명'].values.tolist()
            dict_senator_bills[senator] = list_bills_title
        return dict_senator_bills

    def show_senators_bills_titles(self, senators_list, df_bills):
        dict_senator_bills = {}
        for senator in senators_list:
            senator_name = senator.split(" ", 1)[0]
            bills_id_bySenator = df_bills[df_bills['발의자'].str.contains(senator_name)].bill_id.values.tolist()

            list_temp_keyword_bills_titles = []
            for keyword in user_input:
                bills_id_byKeyword = df_bills.loc[bills_id_bySenator]['bill_id'].values.tolist()
                df_semi = df_bills.loc[bills_id_byKeyword]
                semi_result = df_semi[df_semi['법안명_법안내용'].str.contains(keyword)]['법안명'].drop_duplicates().values.tolist()
                list_temp_keyword_bills_titles.extend(semi_result)
            list_temp_keyword_bills_titles = list(set(list_temp_keyword_bills_titles))
            shuffle(list_temp_keyword_bills_titles)
            print(list_temp_keyword_bills_titles)
            list_bills_titlle = df_bills.loc(list_temp_keyword_bills_titles[:3])
            dict_senator_bills[senator] = list_bills_title
        return dict_senator_bills