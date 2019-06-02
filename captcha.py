import pytesseract
import sys
import argparse
import requests
from bs4 import BeautifulSoup
import datetime
try:
    import Image
except ImportError:
    from PIL import Image
from subprocess import check_output


def resolve(path, sample):
	print("Resampling the Image")
	check_output(['convert', path, '-resample', sample, 'saida.jpeg'])
	return pytesseract.image_to_string(Image.open('saida.jpeg'), lang='eng', config='--oem 3')

if __name__=="__main__":
    '''argparser = argparse.ArgumentParser()
    argparser.add_argument('path',help = 'Captcha file path')
    argparser.add_argument('sample',help = 'Size image')
    '''
    s = requests.session()
    url = "http://www.isbn.bn.br/website/consulta/cadastro"
    h = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'http://www.isbn.bn.br/website/consulta/cadastro/filtrar',
        'Connection': 'keep-alive'
    }
    req = s.get(url)
    jsessionid = s.cookies.get_dict()['JSESSIONID']
    
    h = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0',
        'Accept': 'image/webp,*/*',
        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'http://www.isbn.bn.br/website/consulta/cadastro/filtrar',
        'Connection': 'keep-alive',
        'Cookie': 'JSESSIONID='+jsessionid
    }
    
    data = datetime_object = datetime.datetime.now()
    tempo = int(datetime.datetime.timestamp(data)*1000)
    caminho = 'http://www.isbn.bn.br/website/jcaptcha?'+str(tempo)
    r = s.get(caminho, headers=h)
    open('imagem.jpeg', 'wb').write(r.content)
    
    #args = argparser.parse_args()
    path = 'imagem.jpeg'
    sample = '100'
    print('Resolving Captcha')
    captcha_text = resolve(path,sample).replace(' ','')
    print('Extracted Text',captcha_text)
    
    h = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'http://www.isbn.bn.br/website/consulta/cadastro/filtrar',
        'Connection': 'keep-alive',
        'Cookie': 'JSESSIONID='+jsessionid
    }
    url = 'http://www.isbn.bn.br/website/consulta/cadastro/filtrar'
    req = s.post(url, data={'campo':'1','valor':'9788573289206','imagemCaptcha':captcha_text},headers=h)
    soup = BeautifulSoup(req.text, 'html.parser')
    book = soup.find(name='span',attrs={"id":'imagemCaptcha.errors'})
    if(book == None):
        div = soup.find(name='div',attrs={"class":'conteudo'})
        divs = div.findChildren("div", recursive=False)
        for d in divs:
            if(d.findChildren(name='strong', recursive=False)):
                texto = d.text.strip().replace('ISBN ','').replace('Título ','').replace('Edição ','').replace('Tipo de Suporte ','').replace('Páginas ','').replace('Editor(a) ','').replace('Editor(a) ','').strip()
                print(texto)
    print(book)
    f=open('texto.html','w')
    f.write(req.text)
    f.close()
