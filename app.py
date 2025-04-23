#!/usr/bin/python
# coding=utf-8

import sqlite3
from flask import Flask, render_template, jsonify
import pandas as pd
import json
from jieba.analyse.tfidf import TFIDF
from snownlp import SnowNLP

app = Flask(__name__)
login_name = None

tiebas = []
with open('tieba_info.json', 'r', encoding='utf8') as f:
    for line in f:
        tieba = json.loads(line.strip())
        # 评论情感分析
        tieba['content'] += tieba['title']
        if tieba['content']:
            postive_score = SnowNLP(tieba['content']).sentiments
            tieba['postive_score'] = postive_score
            # 情感极性得分
            tieba['sentiment'] = '正向情感' if postive_score > 0.5 else '负向情感'
            tiebas.append(tieba)

tiebas_df = pd.DataFrame(tiebas, columns=['create_time', 'title', 'link', 'creator', 'content', 'school', 'postive_score', 'sentiment'])
tiebas_df['create_time'] = tiebas_df['create_time'].map(lambda x: x.replace('-02-30', '-02-20'))
tiebas_df = tiebas_df.sort_values(by='create_time', ascending=False)
# tiebas_df = tiebas_df[tiebas_df['create_time'] > '2021-01-01']
tiebas_df['create_time'] = pd.to_datetime(tiebas_df['create_time'])

print(tiebas_df[tiebas_df['school'] == '中央司法警官学院'])
# 中文停用词
STOPWORDS = set(map(lambda x: x.strip(), open('stopwords.txt', encoding='utf8').readlines()))


class WordSegmentPOSKeywordExtractor(TFIDF):

    def extract_sentence(self, sentence, keyword_ratios=None):
        """
        Extract keywords from sentence using TF-IDF algorithm.
        Parameter:
            - keyword_ratios: return how many top keywords. `None` for all possible words.
        """
        words = self.postokenizer.cut(sentence)
        freq = {}

        seg_words = []
        pos_words = []
        for w in words:
            wc = w.word
            seg_words.append(wc)
            pos_words.append(w.flag)

            if len(wc.strip()) < 2 or wc.lower() in self.stop_words:
                continue
            freq[wc] = freq.get(wc, 0.0) + 1.0

        if keyword_ratios is not None and keyword_ratios > 0:
            total = sum(freq.values())
            for k in freq:
                freq[k] *= self.idf_freq.get(k, self.median_idf) / total

            tags = sorted(freq, key=freq.__getitem__, reverse=True)
            top_k = int(keyword_ratios * len(seg_words))
            tags = tags[:top_k]

            key_words = [int(word in tags) for word in seg_words]

            return seg_words, pos_words, key_words
        else:
            return seg_words, pos_words


extractor = WordSegmentPOSKeywordExtractor()


def fetch_keywords(new_title):
    """新闻关键词抽取，保留表征能力强名词和动词"""
    seg_words, pos_words, key_words = extractor.extract_sentence(new_title, keyword_ratios=0.8)
    seg_key_words = []
    for word, pos, is_key in zip(seg_words, pos_words, key_words):
        if pos in {'n', 'nt', 'nd', 'nl', 'nh', 'ns', 'nn', 'ni', 'nz', 'v', 'vd', 'vl', 'vu', 'a'} and is_key:
            if word not in STOPWORDS:
                seg_key_words.append(word)

    return seg_key_words


tiebas_df['title_cut'] = tiebas_df['title'].map(fetch_keywords)


# --------------------- html render ---------------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/news_category')
def news_category():
    return render_template('news_category.html')


@app.route('/tiebas_school')
def tiebas_school():
    return render_template('tiebas_school.html')


@app.route('/hot_words')
def hot_words():
    return render_template('hot_words.html')


@app.route('/sentiment_analysis')
def sentiment_analysis():
    return render_template('sentiment_analysis.html')


@app.route('/tiebas_time_analysis')
def tiebas_time_analysis():
    return render_template('tiebas_time_analysis.html')


# ------------------ ajax restful api -------------------
@app.route('/check_login')
def check_login():
    """判断用户是否登录"""
    return jsonify({'username': login_name, 'login': login_name is not None})


@app.route('/register/<name>/<password>')
def register(name, password):
    conn = sqlite3.connect('user_info.db')
    cursor = conn.cursor()

    check_sql = "SELECT * FROM sqlite_master where type='table' and name='user'"
    cursor.execute(check_sql)
    results = cursor.fetchall()
    # 数据库表不存在
    if len(results) == 0:
        # 创建数据库表
        sql = """
                CREATE TABLE user(
                    name CHAR(256), 
                    password CHAR(256)
                );
                """
        cursor.execute(sql)
        conn.commit()
        print('创建数据库表成功！')

    sql = "INSERT INTO user (name, password) VALUES (?,?);"
    cursor.executemany(sql, [(name, password)])
    conn.commit()
    return jsonify({'info': '用户注册成功！', 'status': 'ok'})


@app.route('/login/<name>/<password>')
def login(name, password):
    global login_name
    conn = sqlite3.connect('user_info.db')
    cursor = conn.cursor()

    check_sql = "SELECT * FROM sqlite_master where type='table' and name='user'"
    cursor.execute(check_sql)
    results = cursor.fetchall()
    # 数据库表不存在
    if len(results) == 0:
        # 创建数据库表
        sql = """
                CREATE TABLE user(
                    name CHAR(256), 
                    password CHAR(256)
                );
                """
        cursor.execute(sql)
        conn.commit()
        print('创建数据库表成功！')

    sql = "select * from user where name='{}' and password='{}'".format(name, password)
    cursor.execute(sql)
    results = cursor.fetchall()

    login_name = name
    if len(results) > 0:
        print(results)
        return jsonify({'info': name + '用户登录成功！', 'status': 'ok'})
    else:
        return jsonify({'info': '当前用户不存在！', 'status': 'error'})


@app.route('/get_tiebas_by_school/<school>')
def get_tiebas_by_school(school):
    cate_df = tiebas_df[tiebas_df['school'] == school]
    cate_df['create_time'] = cate_df['create_time'].map(lambda x: str(x).split(' ')[0])
    return jsonify(cate_df.values.tolist()[:20])


@app.route('/tiebas_words_analysis/<school>')
def tiebas_words_analysis(school):
    cate_df = tiebas_df[tiebas_df['school'] == school]

    word_count = {}
    for key_words in cate_df['title_cut']:
        for word in key_words:
            if word in word_count:
                word_count[word] += 1
            else:
                word_count[word] = 1

    wordclout_dict = sorted(word_count.items(), key=lambda d: d[1], reverse=True)
    wordclout_dict = [{"name": k[0], "value": k[1]} for k in wordclout_dict if k[1] > 3]

    # 选取 top10 的词作为话题词群
    top_keywords = [w['name'] for w in wordclout_dict[:10]][::-1]
    top_keyword_counts = [w['value'] for w in wordclout_dict[:10]][::-1]

    return jsonify({'词云数据': wordclout_dict, '词群': top_keywords, '词群个数': top_keyword_counts})


@app.route('/tieba_time_vis/<school>')
def tieba_time_vis(school):
    """ 时间维度分析 """
    school_df = tiebas_df[tiebas_df['school'] == school]
    school_df['create_time'] = school_df['create_time'].dt.date
    daily_counts = school_df[['create_time', 'title']].groupby(by='create_time').count().reset_index()
    return jsonify({'日期': daily_counts['create_time'].astype(str).values.tolist(),
                    '贴数': daily_counts['title'].values.tolist()})


@app.route('/sentiment_pie_analysis')
def sentiment_pie_analysis():
    """高校的情感极性分布情况"""
    schools = set(tiebas_df['school'].values.tolist())

    school_sentiment_count = {}
    for school in schools:
        school_df = tiebas_df[tiebas_df['school'] == school]
        sent_count = school_df[['sentiment', 'create_time']].groupby(by='sentiment').count().reset_index()
        school_sentiment_count[school] = {
            '正向情感': sent_count[sent_count['sentiment'] == '正向情感']['create_time'].values.tolist()[0],
            '负向情感': sent_count[sent_count['sentiment'] == '负向情感']['create_time'].values.tolist()[0]
        }

    print(school_sentiment_count)
    return jsonify({
        '高校': list(schools),
        '情感极性': school_sentiment_count
    })


if __name__ == "__main__":
    app.run(host='127.0.0.1')
