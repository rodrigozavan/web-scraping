from urllib.request import urlopen, Request, urlretrieve
from urllib. error import  URLError, HTTPError
from bs4 import BeautifulSoup
import pandas as pd
import datetime

#Para alguns sites é necessário utilizar o Request e passar o parêmetro do user agente para simular o
# acesso como um navegador

# Trata espaços do html
def treatHtml(entrada):
    return " ".join(entrada.split()).replace('> <', '><')

# Coleta html da URL
def getHtml(url):
    try:
        url = url
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0'}
        req = Request(url, headers=headers)
        response = urlopen(req)
        html = response.read()
        html = html.decode('utf-8')
        return html
    except HTTPError as e: # Tratamento de erros HTTP
        error = str(e.code) + ' ' + str(e.reason)
        return error
    except URLError as e: # Tratamento de erros URL
        error = str(e.reason)
        return error

url = 'https://alura-site-scraping.herokuapp.com/index.php?page=1'
html = treatHtml(getHtml(url))
soup = BeautifulSoup(html, 'html.parser')

pages = int(str(soup.find('span', {'class': 'info-pages'}).get_text()).split()[-1])
cards = []

print('Iniciado ', datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
for i in range(pages):
    url = f'https://alura-site-scraping.herokuapp.com/index.php?page={i+1}'
    html = treatHtml(getHtml(url))
    soup = BeautifulSoup(html, 'html.parser')
    anuncios = soup.find('div', {'id':'container-cards'}).findAll('div', {'class':'well card'})
    for anuncio in anuncios:
        card = {}
        # Valor
        card['value'] = anuncio.find('p', {'class': 'txt-value'}).getText()

        # Informações
        infos = anuncio.find('div', {'class': 'body-card'}).findAll('p')
        for info in infos:
            card[info.get('class')[0].split('-')[-1]] = info.get_text()

        # Acessórios
        items = anuncio.find('div', {'class': 'body-card'}).ul.findAll('li')
        items.pop()
        acessorios = []
        for item in items:
            acessorios.append(item.get_text().replace('► ', ''))
        card['items'] = acessorios

        # Adicionando card
        cards.append(card)

        # Imagens
        image = anuncio.find('div', {'class': 'image-card'}).img
        urlretrieve(image.get('src'), './output/img/' + image.get('src').split('/')[-1])

dataset = pd.DataFrame(cards)
dataset.to_csv('./output/data/carros.csv', index=False, encoding='utf-8-sig', sep=';')
print('Finalizado ', datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))