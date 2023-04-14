'''
home post type-post category-italia 

home post type-post category-bits

archive arc-flashes closed flashes type-flashes tag-arnold-schwarzenegger selected current

archive arc-flashes closed flashes type-flashes
'''
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
pages=['https://ilpost.it', 'https://www.ilpost.it/bits/', 'https://www.ilpost.it/flashes/']

home_request = requests.get(pages[0])
#bits_request=requests.get(pages[1])
#flashes_request=requests.get(pages[2])

def sendArticle(title, headline, link):
    method='/sendMessage'
    text='*'+title+'*\n\n_'+headline+'_\n'+link
    data = {'chat_id': chatid, 'text': text, 'parse_mode': 'Markdown'}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(base+token+method, json=data, headers=headers)
    print(r.content)

def contentProcessing(scan, page):
    articles=dict()
    for article in scan.find_all('article'):
        if page in article['class']:
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
    return articles


#reading latest scrape results
f = open("latest_article.txt", "r")
latest=json.loads(f.read())
f.close()

#scanning articles to retrieve information
#print(bits_request.headers)
scan=BeautifulSoup(home_request.content.decode(encoding='utf-8'), features="html.parser")
#scan_bits=BeautifulSoup(bits_request.content.decode(encoding='utf-8'), features="html.parser")
#print(scan)
articles=dict()
articles=contentProcessing(scan, "home")
#articles_bits=contentProcessing(scan_bits, "bits")
#print(articles_bits)


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