import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import konlpy
from konlpy.tag import Mecab
from sklearn.manifold import TSNE
import fasttext
import time
import json
from tqdm import tqdm
from gensim.models import Word2Vec, FastText
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


mecab = Mecab()
def tokenized_mecab(data):
    result = mecab.morphs(data)
    result = ' '.join(result)
    return result

def out_stopwords(data):
    data = data.split(" ")
    stopwords = ['등','으로','하','는','은','이','가','의','을','를','「','」','에게','고','있','으나',',',
            '로','적','어','한','이','할','수','있','어','하','기','가','.','에','등','을','로','하','거나',
            '에','(',')','1','제','의','조','항','.','-','·',"'",'년','월','일','및','%','?']
    data = [token for token in data if token not in stopwords]
    return data

# 법안과 cleared 내용으로 key, value 매치
bills_json = {}
for idx in list(range(bills.shape[0])):
    temp_dict = {}
    temp_dict['bill_id'] = int(bills['bill_id'].iloc[idx])
    temp_dict['법안명'] = bills['법안명'].iloc[idx]
    temp_dict['cleared_token'] = bills['cleared'].iloc[idx]
    bills_json[int(bills['bill_id'].iloc[idx])] = temp_dict

tokenized = ''
for content in temp['cleared'].values:
    tokenized = tokenized + "{} \n".format(content)
corpus = [sent.strip().split(" ") for sent in tokenized.split('\n')]

# 학습하기
start = time.time()
embedding_model = Word2Vec(corpus, size=100, window = 3, min_count=30, workers=5, iter=10, sg=1)
print("time :", time.time() - start)

# word와 vector dictionary로 묶기
word_dict = {}
for vocab, vector in zip(embedding_model.wv.index2word, embedding_model.wv.vectors):
    word_dict[vocab] = vector

# TF-IDF dictionary 만들기
tfidf = TfidfVectorizer()
tfidf_score = tfidf.fit_transform(temp['cleared'])
tfidf_feature_names = tfidf.get_feature_names()

# TF-IDF score 저장해주기
tfidf_dict = {}
for idx, val in zip(tfidf_score.indices, tfidf_score.data):
    word = tfidf_feature_names[idx]
    tfidf_dict[word] = val


# 법안별 유사도 찾기
similarity = {}
target_bill = '0'
for item in bills_json:
    if item != target_bill:
        sim = cosine_similarity(np.array(bills_json[target_bill]['vector']).reshape(1,-1), np.array(bills_json[item]['vector']).reshape(1,-1))
        similarity[bills_json[item]['법안명']] = float(sim)
similarity = {key: value for key, value in sorted(similarity.items(), key=lambda item: item[1], reverse=True)}
rating = [key for key, value in sorted(similarity.items(), key=lambda item: item[1], reverse=True)]

# 뒤에 아직 한참 남음