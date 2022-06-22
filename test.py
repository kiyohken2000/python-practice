import requests
import spacy
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import geocoder

def hello_pubsub(event, context):
       cred = credentials.Certificate('serviceAccountKey.json')
       firebase_admin.initialize_app(cred)

       db = firestore.client()

       # モデルのロード
       nlp = spacy.load("ja_core_news_md")

       # yahooのサイトから情報取得
       response = requests.get('https://news.yahoo.co.jp/search?p=%23安倍晋三&ei=UTF-8')
       # レスポンスを成形
       html = BeautifulSoup(response.content, 'html.parser')
       # 特定のキーワードを抽出
       i = 1
       articles = []
       for a in html.select('.newsFeed a'):
       # 出力処理
       # print(a['href'], list(a.strings)[0])
              response = requests.get(a['href'])
              html = BeautifulSoup(response.content, 'html.parser')

              title = html.select('#contentsWrap h1')[0].contents[0]
              time = html.select('time')[0].text
              url = a['href']
              print('------------------')
              print('記事のタイトル: ', title)
              print('配信日時: ', time)
              print('------------------')
              # print(data)
              data = {}

              body = html.select('.article_body.highLightSearchTarget p')
              
              # bodyStrings = p.sub("", body[1])
              # モデルに解析対象のテキストを渡す
              doc = nlp(body[1].text)
              sample_text = body[1].text

              # 固有表現を抽出
              tags = []
              for ent in doc.ents:
                     # print(ent.text, ent.label_)
                     # tags.append(ent.text)

                     locationData= {}
                     if ent.label_ == 'GPE':
                            # print(ent.text, ent.label_)
                            tags.append(ent.text)

              preTags = list(set(tags))

              positions = []
              for tag in preTags:
                     location = {}
                     ret = geocoder.osm(tag, timeout=5.0)
                     location['label'] = tag
                     location['position'] = ret.latlng
                     if ret.latlng != None:
                            positions.append(location)

              data['title'] = title
              data['time'] = time
              data['url'] = url
              data['positions'] = positions
              articles.append(data)
              if i >= 10 :
                     break
              i = i + 1
       
       # print(articles)

       doc_ref = db.collection(u'trace').document(u'articles')
       doc_ref.set({
       u'articles': articles
       })