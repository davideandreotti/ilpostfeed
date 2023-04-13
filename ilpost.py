import requests
from bs4 import BeautifulSoup
import json
base='https://api.telegram.org/bot'
f = open("token", "r")
token=f.read()
f.close()

#token=''
admin='25679064'
chatid='-1001216458621'
x = requests.get('https://ilpost.it')
def sendArticle(title, headline, link):
    method='/sendMessage'
    text='*'+title+'*\n\n_'+headline+'_\n'+link
    data = {'chat_id': chatid, 'text': text, 'parse_mode': 'Markdown'}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(base+token+method, json=data, headers=headers)
    print(r.content)

#reading latest scrape results
f = open("latest_article.txt", "r")
latest=json.loads(f.read())
f.close()

#scanning articles to retrieve information
scan=BeautifulSoup(x.content.decode(encoding='utf-8'), 'html')
articles=dict()
for article in scan.find_all('article'):
    if 'home' in article['class']:
        elements=dict()
        id=article['id']
        elements['id']=id
        #print(id)
        elements['img_url']=article.find('img')['src']
        #print(img_url)
        content=article.find("div", {"class": "entry-content"})
        elements['title'] = content.h2.a['title']
        elements['headline'] = content.p.a['title']
        elements['link']=content.h2.a['href'].split('?')[0]
        articles[id]=elements

#merging old vs new scrape
sorted_ids=list(articles.keys())
sorted_ids.sort()
sorted_articles = {i: articles[i] for i in sorted_ids}
for id in sorted_ids:
    if id not in latest:
        elements=sorted_articles[id]
        #sending to telegram
        #print(elements['title'], elements['headline'], elements['link'])
        sendArticle(elements['title'], elements['headline'], elements['link'])

f = open("latest_article.txt", "w")
f.write(json.dumps(sorted_ids))
f.close()