import requests
from bs4 import BeautifulSoup
import json
base='https://api.telegram.org/bot'
f = open("token", "r")
token=f.read()
f.close()

#token=''
admin='25679064'
#chatid='25679064'
chatid='-1001216458621'
pages=['https://ilpost.it', 'https://www.ilpost.it/bits/', 'https://www.ilpost.it/flashes/']

home_request = requests.get(pages[0])
bits_request=requests.get(pages[1])
flashes_request=requests.get(pages[2])
#print(bits_request.content)

def sendArticle(title, headline, link, section):
    method='/sendMessage'
    if(section=='home'):
        emoji='\U0001F4F0' 
    elif (section=='bits'):
        emoji='\U00002728'
    else:
        emoji='\U000026A1'
    text='*'+title+'*\n\n_'+headline+'_\n'+emoji+' '+link
    data = {'chat_id': chatid, 'text': text, 'parse_mode': 'Markdown'}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(base+token+method, json=data, headers=headers)
    print(r.content)

def contentProcessing(scan, page):
    articles=dict()
    for article in scan.find_all('article'):
        if 'home' in article['class']:
            elements=dict()
            id=article['id']
            if 'adv' in id:
                continue
            elements['id']=id
            elements['img_url']=article.find('img')['src']
            content=article.find("div", {"class": "entry-content"})
            elements['title'] = content.h2.a['title']
            if page == 'home':
                elements['headline'] = content.p.a['title']
            elif page == 'bits':
                elements['headline'] = content.div.a.text+' | '+content.div.span.text
            elements['section'] = page
            elements['link']=content.h2.a['href'].split('?')[0]
            #if strange link report html to admin
            if elements['link']=='https://www.ilpost.it/':
                data = {'chat_id': admin, 'text': "Link leads to homepage!\n"+str(article)}
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                r = requests.post(base+token+'/sendMessage', json=data, headers=headers)
            if((elements['title'] == elements['headline']) or (elements['headline'] == elements['link']) or (elements['title'] == elements['link'])):
                data = {'chat_id': admin, 'text': "Repeated argument!\n"+str(article)}
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                #r = requests.post(base+token+'/sendMessage', json=data, headers=headers)
            articles[id]=elements
    return articles
def flashesProcessing(scan):
    articles=dict()
    for article in scan.find_all('article'):
        if 'flashes' in article['class']:
            elements=dict()
            id=article['id']
            elements['id']=id
            #print(id)
            elements['img_url']=article.find('img')['src']
            #print(img_url)
            elements['title']=article.div['data-posttitle']
            elements['headline'] = article.div.div.a['href'] + '\n' + article.div.div.time['datetime']
            elements['section'] = 'flashes'
            elements['link']=article.div.h2.a['href']
            articles[id]=elements
    return articles


#reading latest scrape results
f = open("latest_article.txt", "r")
latest=json.loads(f.read())
f.close()

#scanning articles to retrieve information
#print(bits_request.headers)
scan=BeautifulSoup(home_request.content.decode(encoding='utf-8'), features="html.parser")
scan_bits=BeautifulSoup(bits_request.content.decode(encoding='utf-8'), features="html.parser")
scan_flashes=BeautifulSoup(flashes_request.content.decode(encoding='utf-8'), features="html.parser")

#print(scan)
articles=contentProcessing(scan, "home")
articles_bits=contentProcessing(scan_bits, "bits")
articles_flashes = flashesProcessing(scan_flashes)
#print(articles_flashes)

#merge lists
articles.update(articles_bits)
articles.update(articles_flashes)
#print(articles)




#merging old vs new scrape
sorted_ids=list(articles.keys())
sorted_ids.sort()
sorted_articles = {i: articles[i] for i in sorted_ids}
for id in sorted_ids:
    if id not in latest:
        elements=sorted_articles[id]
        #sending to telegram
        #print(elements['title'], elements['headline'], elements['link'], elements['section'])
        sendArticle(elements['title'], elements['headline'], elements['link'], elements['section'])

f = open("latest_article.txt", "w")
f.write(json.dumps(sorted_ids))
f.close()