import time
import json
import numpy as np
import pandas as pd
from tqdm import tqdm
tqdm.pandas()
from random import shuffle
from konlpy.tag import Mecab
from collections import Counter
from gensim.models import Word2Vec, FastText, Doc2Vec

class Preprocess_to_Train:
    def __init__(self, df_bills, df_senators):
        self.bills = df_bills
        self.senators = df_senators

    def tokenized_mecab(self, data):
        mecab = Mecab()
        result = mecab.morphs(data)
        result = ' '.join(result)
        return result

    def preprocess(self, url):
        bills = self.bills
        bills['tokenized'] = bills['법안명_법안내용'].apply(self.tokenized_mecab)

        bills = self.remove_stopwords(bills, url)
        result = bills
        return result
    
    def make_stopwords_list(self, url):
        stopwords_file = list(open(url,"r"))
        list_stopword = []
        for i in stopwords_file:
            list_stopword.append(i[:-1])
        return list_stopword

    def out_stopwords(self, data, list_stopwords):
        data = data.split(" ")
        list_stopwords = list_stopwords
        data = [token for token in data if token not in list_stopwords]
        return data
        
    def remove_stopwords(self, df, url):
        bills = df
        list_stopword = self.make_stopwords_list(url = url)
        bills['cleared'] = bills['tokenized'].apply(lambda x: self.out_stopwords(x, list_stopwords = list_stopword))    # stopwords 없애기
        bills['cleared'] = [' '.join(map(str, l)) for l in bills['cleared']]   # list로 쌓여있던 value들을 꺼내서 string으로 만들기
        result = bills
        return result

    def train_w2v(self, df, iteration):
        # 학습에 필요한 corpus 만들기
        tokenized = ''
        bills = df
        for content in bills['cleared'].values:
            tokenized = tokenized + "{} \n".format(content)
        corpus = [sent.strip().split(" ") for sent in tokenized.split('\n')]
        embedding_model = Word2Vec(corpus, size=100, window = 3, min_count=10,  
                                workers=5, iter=iteration, hs=0, sg=1)
        return embedding_model

    def make_word_vector_dict(self, df, iteration):
        embedding_model = self.train_w2v(df, iteration)
        word_dict = {}
        for vocab, vector in zip(embedding_model.wv.index2word, embedding_model.wv.vectors):
            word_dict[vocab] = vector
        return word_dict

    def get_n_save_bills_vector(self, df, iteration, dir_):
        # 법안과 cleared 내용으로 key, value 매치
        bills = df
        bills_json = {}
        word_dict = self.make_word_vector_dict(bills, iteration)
        for idx in range(bills.shape[0]):
            temp_dict = {}
            temp_dict['bill_id'] = int(bills['bill_id'].iloc[idx])
            temp_dict['법안명'] = bills['법안명'].iloc[idx]
            temp_dict['cleared_token'] = bills['cleared'].iloc[idx]
            bills_json[str(bills['bill_id'].iloc[idx])] = temp_dict
        
        for idx in bills_json:
            list_vector =[]
            for word in bills_json[idx]['cleared_token'].split():
                if word in word_dict.keys():
                    list_vector.append(word_dict[word])
            bills_json[idx]['vector'] = np.sum(list_vector, axis=0).tolist()
        
        with open(dir_, 'w', encoding='utf-8') as make_file:
            json.dump(bills_json, make_file, indent="\t")
        return bills_json
    
    def get_n_save_senators_vector(self, df_senators, df_bills, json_bills, dir_):
        senators = df_senators
        bills = df_bills
        bills_json = json_bills
        # 의원데이터 전처리
        senators['한글이름'] = senators['이름'].str.split(' ').str[0]
        senators['한자이름'] = senators['이름'].str.split(' ').str[1]

        # 의원들 json 파일로 만들어주기
        senators_json = {}
        for idx in list(range(senators.shape[0])):
            temp_dict = {}
            temp_dict['한글이름'] = senators['한글이름'].iloc[idx]
            temp_dict['한자이름'] = senators['한자이름'].iloc[idx]
            temp_dict['정당'] = senators['정당'].iloc[idx]
            senators_json[senators['이름'].iloc[idx]] = temp_dict    

        # 의원들 vector 계산하기 (동명이인은 따로 계산해줘야 함)
        for idx in range(senators.shape[0]):
            full_name = senators['이름'].iloc[idx]
            chinese_name = senators['한자이름'].iloc[idx]
            korean_name = senators['한글이름'].iloc[idx]

            # 발의에 참여한 법안들 모으기
            participated_bills = list(bills[bills['발의자'].str.contains(korean_name)]['bill_id'].values)

            bill_vector_list = []
            for bill_id in participated_bills:
                bill_vector_list.append(np.array(bills_json[str(bill_id)]['vector']))
            senators_json[full_name]['vector'] = (np.sum(bill_vector_list, axis=0)/len(bill_vector_list)).tolist()

        with open(dir_, 'w', encoding='utf-8') as make_file:
            json.dump(senators_json, make_file, indent="\t")
        return senators_json