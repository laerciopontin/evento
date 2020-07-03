import urllib3
import nltk
#nltk.download()
import pymysql
import re 
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def inserePalavraLocalizacao(idurl, idpalavra, localizacao):
    #função para inserir localizacao da palavra
    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice', autocommit = True, use_unicode = True, charset = 'utf8mb4')
    cursor = conexao.cursor()
    print('insert into palavra_localizacao (idurl, idpalavra, localizacao) values ( ' + str(idurl)+', ' + str(idpalavra)+ ', ' + str(localizacao)+')')
    cursor.execute('insert into palavra_localizacao (idurl, idpalavra, localizacao) values (%s, %s, %s)', (idurl, idpalavra, localizacao))
    idpalavralocalizacao = cursor.lastrowid
    cursor.close()
    conexao.close()
    return idpalavralocalizacao

def palavraIndexada(palavra):
    #verifica se já existe a palavra na base
    retorno = -1 #não existe a palavra na base
    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice')
    cursor = conexao.cursor()
    cursor.execute('select idpalavra from palavras where palavra = %s', palavra)
    if cursor.rowcount > 0:
        retorno = cursor.fetchone()[0] #já existe a palavra na base
    cursor.close()
    conexao.close()
    return retorno

def inserePalavra(palavra):
    #função para inserir nova palavra
    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice', autocommit = True, use_unicode = True, charset = 'utf8mb4')
    cursor = conexao.cursor()
    print('insert into palavras (palavra) values (' + str(palavra)+')')
    cursor.execute('insert into palavras (palavra) values (%s)', palavra)
    idpalavra = cursor.lastrowid
    cursor.close()
    conexao.close()
    return idpalavra

def insereUrlLigacao(idurl_origem, idurl_destino):
    #função de relacionamento entre urls relacionadas (com mesmas palavras)
    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice', autocommit = True, use_unicode = True, charset = 'utf8mb4')
    cursor = conexao.cursor()
    #print('insert into url_ligacao (idurl_origem, idurl_destino) values (%s, %s)', (idurl_origem, idurl_destino)+')')
    cursor.execute('insert into url_ligacao (idurl_origem, idurl_destino) values (%s, %s)', (idurl_origem, idurl_destino))
    idurl_ligacao = cursor.lastrowid
    cursor.close()
    conexao.close()
    return idurl_ligacao


def insereUrlPalavra(idpalavra, idurl_ligacao):
    #função de relacionamento as palavras pertencentes as urls
    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice', autocommit = True, use_unicode = True, charset = 'utf8mb4')
    cursor = conexao.cursor()
    #print('insert into url_ligacao (idurl_origem, idurl_destino) values (%s, %s)', (idurl_origem, idurl_destino)+')')
    cursor.execute('insert into url_palavra (idpalavra, idurl_ligacao) values (%s, %s)', (idpalavra, idurl_ligacao))
    idurl_palavra = cursor.lastrowid
    cursor.close()
    conexao.close()
    return idurl_palavra


def getIdUrlLigacao(idurl_origem, idurl_destino):
    idurl_ligacao = -1
    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice', autocommit = True, use_unicode = True, charset = 'utf8mb4')
    cursor = conexao.cursor()
    #print('insert into url_ligacao (idurl_origem, idurl_destino) values (%s, %s)', (idurl_origem, idurl_destino)+')')
    cursor.execute('select idurl_ligacao from url_ligacao where idurl_origem = %s and idurl_destino = %s', (idurl_origem, idurl_destino))
    if cursor.rowcount >0:
        idurl_ligacao = cursor.fetchone()[0]
    cursor.close()
    conexao.close()
    return idurl_ligacao

def getIdUrl(url):
    idurl = -1 #não existe a página
    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice', use_unicode = True, charset = 'utf8mb4')
    cursorUrl = conexao.cursor()
    cursorUrl.execute('select idurl from urls where url = %s', url)
    if cursorUrl.rowcount > 0 :
        #print("Url cadastrada!")
        idurl = cursorUrl.fetchone()[0]
        
    cursorUrl.close()
    conexao.close()
    return idurl

def paginaIndexada(url):
    #função para buscar página indexada
    retorno = -1 #não existe a página
    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice', use_unicode = True, charset = 'utf8mb4')
    cursorUrl = conexao.cursor()
    cursorUrl.execute('select idurl from urls where url = %s', url)
    if cursorUrl.rowcount > 0 :
        #print("Url cadastrada!")
        idurl = cursorUrl.fetchone()[0]
        cursorPalavra = conexao.cursor()
        cursorPalavra.execute('select idurl from palavra_localizacao where idurl = %s', idurl)
        if cursorPalavra.rowcount > 0:
           retorno = -2 #existe a página com palavras cadastradas 
        else:            
           retorno = -2 #existe a página sem palavras cadastradas
        cursorPalavra.close()
    cursorUrl.close()
    conexao.close()
    return retorno
    
def inserePagina(url):
    #função para indexar nova página
    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice', autocommit = True, use_unicode = True, charset = 'utf8mb4')
    cursor = conexao.cursor()
    print('insert into urls (url) values (' + str(url)+')')
    cursor.execute('insert into urls (url) values (%s)', url.lower())
    idpagina = cursor.lastrowid
    cursor.close()
    conexao.close()    
    return idpagina


def separaPalavras(texto):    
    stop = nltk.corpus.stopwords.words('portuguese')
    #biblioteca com lista de palavras ditas stopwords     
    splitter = re.compile('\\W+')
    #pega apenas palavras, retirando caracteres que não sejam (diminui a numerosidade)    
    stemmer = nltk.stem.RSLPStemmer()
    #biblioteca que extrai o radical das palavras (diminui a dimensionalidade)    
    lista_palavras = []
    lista = [p for p in splitter.split(texto) if p != ' ']
    #percorre todas as palavras de um texto e quebra as palavras desconsiderando os espaços vazios !=' '
    for p in lista:
        if p.lower() not in stop:
        #não insere na lista palavras ditas stopwords
            if len(p) > 1:
            #retira palavras com 1 caracter    
                lista_palavras.append(stemmer.stem(p).lower())
                #carrega os radicais da palavras na lista 
    return lista_palavras

def urlLigaPalavra(url_origem, url_destino):
    palavras = separaPalavras(url_destino)
    idurl_origem = getIdUrl(url_origem)
    idurl_destino = getIdUrl(url_destino)    
    if idurl_destino == -1:
        idurl_destino = inserePagina(url_destino)
    
    if idurl_origem == idurl_destino:
        return
    
    if getIdUrlLigacao(idurl_origem, idurl_destino)>0:
        return
    
    idurl_ligacao = insereUrlLigacao(idurl_origem, idurl_destino)
    
    for palavra in palavras:
        idpalavra = palavraIndexada(palavra)
        if palavra == -1:
            idpalavra = inserePalavra(palavra)
    
    insereUrlPalavra(idpalavra, idurl_ligacao)

#teste = separaPalavras('Teste aleatório, para restar a classificação, obrigado! 01/01/2020')

def getText(sopa):
    ##função para remover tags html e js
    for tags in sopa(['script', 'style']):
        tags.decompose()
    return ' '.join(sopa.stripped_strings)
    ##remove espaços em branco entre strings

def indexador(url, sopa):
    #verifica e insere valores na base de dados
    indexada = paginaIndexada(url)
    #verifica se existe a página no banco e processa
    if indexada == -2:
        print('Url já cadastrada')
        return
    elif indexada == -1:
        idnovaPagina = inserePagina(url)
    elif indexada > 0:
        idnovaPagina = indexada
        
    print('Indexando' + url)
    
    texto = getText(sopa)
    palavras = separaPalavras(texto)
    
    for i in range(len(palavras)):
        #verifica se existe a palavra na base e processa
        palavra = palavras[i]
        idPalavra = palavraIndexada(palavra)
        if idPalavra == -1:
            idPalavra = inserePalavra(palavra)
            
        inserePalavraLocalizacao(idnovaPagina, idPalavra, i)
        #insere a localização da palavra
        
def crawl(paginas, profundidade):
    ##cria função crawl
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager()
    #classe que busca dados de várias páginas web
    for i in range(profundidade):
        #controla a profundidade de paginas a ser buscada
        novas_paginas = set()
        #conjunto sem valores repetidos
        
        for pagina in paginas:
            #faz a varredura na lista de paginas passadas no argumento
            try:
                dados_pagina = http.request('GET', pagina)
            except:
                print('Erro ao abrir a página '+ pagina)
                continue
            
            sopa = BeautifulSoup(dados_pagina.data, 'lxml')
            
            indexador(pagina, sopa)
            #popula as páginas no banco
            links = sopa.find_all('a')
            contador = 0
            for link in links:
               # print(str(link.contents)+ ' - ' + str(link.get('href')))
               #print(link.attrs)
               #demonstra quais atributos existem dentro dos links
               #print('\n')
               #salta linha       
               if('href' in link.attrs):
                   #verifica se de fato traz o link
                   url = urljoin(pagina, str(link.get('href')))
                   #verifica se existe http na url, para conseguir acessar
                   #o site
                   #if url!= link.get('href'):
                   #    #apenas para demonstrar a correção do link
                   #    print(url)
                   #    print(link.get('href'))
                   if url.find("'")!= -1:
                       #retira url que tem apenas o '
                       continue
                   
                   #print(url)
                   url = url.split('#')[0]
                   #print(url)
                   #corrige urls de navegação internas da página
                   
                   if url[0:4]=='http':
                       novas_paginas.add(url)
                   urlLigaPalavra(pagina, url)
                       #adiciona os novos links na lista de percorrimento
                   contador= contador+1
            paginas = novas_paginas
            #atualiza valor de paginas, para que percorra novas urls identificadas
            #print(contador)
       
listapaginas = [#'https://novaescola.org.br/plano-de-aula']
        'http://basenacionalcomum.mec.gov.br/abase',
                'http://basenacionalcomum.mec.gov.br/abase/apresentacao',
                'http://basenacionalcomum.mec.gov.br/abase/a-base-nacional-comum-curricular',
                'http://basenacionalcomum.mec.gov.br/abase/competencias-gerais-da-base-nacional-comum-curricular',
                'http://basenacionalcomum.mec.gov.br/abase/os-marcos-legais-que-embasam-a-bncc',
                'http://basenacionalcomum.mec.gov.br/abase/os-fundamentos-pedagogicos-da-bncc',
                'http://basenacionalcomum.mec.gov.br/abase/o-pacto-interfederativo-e-a-implementacao-da-bncc',
                'http://basenacionalcomum.mec.gov.br/abase/estrutura',
                'http://basenacionalcomum.mec.gov.br/abase/a-educacao-infantil-na-base-nacional-comum-curricular',
                'http://basenacionalcomum.mec.gov.br/abase/a-educacao-infantil-no-contexto-da-educacao-basica',
                'http://basenacionalcomum.mec.gov.br/abase/direitos-de-aprendizagem-e-desenvolvimento-na-educacao-infantil',
                'http://basenacionalcomum.mec.gov.br/abase/os-campos-de-experiencias',
                'http://basenacionalcomum.mec.gov.br/abase/os-objetivos-de-aprendizagem-e-desenvolvimento-para-a-educacao-infantil',
                'http://basenacionalcomum.mec.gov.br/abase/a-transicao-da-educacao-infantil-para-o-ensino-fundamental',
                'http://basenacionalcomum.mec.gov.br/abase/fundamental',
                'http://basenacionalcomum.mec.gov.br/abase/o-ensino-fundamental-no-contexto-da-educacao-basica',
                'http://basenacionalcomum.mec.gov.br/abase/a-area-de-linguagens',
                'http://basenacionalcomum.mec.gov.br/abase/competencias-especificas-de-linguagens-para-o-ensino-fundamental',
                'http://basenacionalcomum.mec.gov.br/abase/lingua-portuguesa',
                'http://basenacionalcomum.mec.gov.br/abase/competencias-especificas-de-lingua-portuguesa-para-o-ensino-fundamental',
                'http://basenacionalcomum.mec.gov.br/abase/lingua-portuguesa-no-ensino-fundamental-anos-iniciais-praticas-de-linguagem-objetos-de-conhecimento-e-habilidades',
                'http://basenacionalcomum.mec.gov.br/abase/lingua-portuguesa-no-ensino-fundamental-anos-finais-praticas-de-linguagem-objetos-de-conhecimento-e-habilidades',
                'http://basenacionalcomum.mec.gov.br/abase/arte',
                'http://basenacionalcomum.mec.gov.br/abase/competencias-especificas-de-arte-para-o-ensino-fundamental',
                'http://basenacionalcomum.mec.gov.br/abase/arte-no-ensino-fundamental-anos-iniciais-unidades-tematicas-objetos-de-conhecimento-e-habilidades',
                'http://basenacionalcomum.mec.gov.br/abase/arte-no-ensino-fundamental-anos-finais-unidades-tematicas-objetos-de-conhecimento-e-habilidades',
                'http://basenacionalcomum.mec.gov.br/abase/educacao-fisica',
                'http://basenacionalcomum.mec.gov.br/abase/competencias-especificas-de-educacao-fisica-para-o-ensino-fundamental',
                'http://basenacionalcomum.mec.gov.br/abase/educacao-fisica-no-ensino-fundamental-anos-iniciais-unidades-tematicas-objetos-de-conhecimento-e-habilidades',
                'http://basenacionalcomum.mec.gov.br/abase/educacao-fisica-no-ensino-fundamental-anos-finais-unidades-tematicas-objetos-de-conhecimento-e-habilidades',
                'http://basenacionalcomum.mec.gov.br/abase/lingua-inglesa',
                'http://basenacionalcomum.mec.gov.br/abase/competencias-especificas-de-lingua-inglesa-para-o-ensino-fundamental',
                'http://basenacionalcomum.mec.gov.br/abase/lingua-inglesa-no-ensino-fundamental-anos-finais-unidades-tematicas-objetos-de-conhecimento-e-habilidades',
                'http://basenacionalcomum.mec.gov.br/abase/a-area-de-matematica',
                'http://basenacionalcomum.mec.gov.br/abase/competencias-especificas-de-matematica-para-o-ensino-fundamental',
                'http://basenacionalcomum.mec.gov.br/abase/matematica',
                'http://basenacionalcomum.mec.gov.br/abase/matematica-no-ensino-fundamental-anos-iniciais-unidades-tematicas-objetos-de-conhecimento-e-habilidades',
                'http://basenacionalcomum.mec.gov.br/abase/matematica-no-ensino-fundamental-anos-finais-unidades-tematicas-objetos-de-conhecimento-e-habilidades',
                'http://basenacionalcomum.mec.gov.br/abase/a-area-de-ciencias-da-natureza',
                'http://basenacionalcomum.mec.gov.br/abase/competencias-especificas-de-ciencias-da-natureza-para-o-ensino-fundamental',
                'http://basenacionalcomum.mec.gov.br/abase/ciencias',
                'http://basenacionalcomum.mec.gov.br/abase/ciencias-no-ensino-fundamental-anos-iniciais-unidades-tematicas-objetos-de-conhecimento-e-habilidades',
                'http://basenacionalcomum.mec.gov.br/abase/ciencias-no-ensino-fundamental-anos-finais-unidades-tematicas-objetos-de-conhecimento-e-habilidades',
                'http://basenacionalcomum.mec.gov.br/abase/a-area-de-ciencias-humanas',
                'http://basenacionalcomum.mec.gov.br/abase/competencias-especificas-de-ciencias-humanas-para-o-ensino-fundamental',
                'http://basenacionalcomum.mec.gov.br/abase/geografia',
                'http://basenacionalcomum.mec.gov.br/abase/competencias-especificas-de-geografia-para-o-ensino-fundamental',
                'http://basenacionalcomum.mec.gov.br/abase/geografia-no-ensino-fundamental-anos-iniciais-unidades-tematicas-objetos-de-conhecimento-e-habilidades',
                'http://basenacionalcomum.mec.gov.br/abase/geografia-no-ensino-fundamental-anos-finais-unidades-tematicas-objetos-de-conhecimento-e-habilidades',
                'http://basenacionalcomum.mec.gov.br/abase/historia',
                'http://basenacionalcomum.mec.gov.br/abase/competencias-especificas-de-historia-para-o-ensino-fundamental',
                'http://basenacionalcomum.mec.gov.br/abase/historia-no-ensino-fundamental-anos-iniciais-unidades-tematicas-objetos-de-conhecimento-e-habilidades',
                'http://basenacionalcomum.mec.gov.br/abase/historia-no-ensino-fundamental-anos-finais-unidades-tematicas-objetos-de-conhecimento-e-habilidades',
                'http://basenacionalcomum.mec.gov.br/abase/a-area-de-ensino-religioso',
                'http://basenacionalcomum.mec.gov.br/abase/competencias-especificas-de-ensino-religioso-para-o-ensino-fundamental',
                'http://basenacionalcomum.mec.gov.br/abase/ensino-religioso',
                'http://basenacionalcomum.mec.gov.br/abase/ensino-religioso-no-ensino-fundamental-anos-iniciais-unidades-tematicas-objetos-de-conhecimento-e-habilidades',
                'http://basenacionalcomum.mec.gov.br/abase/ensino-religioso-no-ensino-fundamental-anos-finais-unidades-tematicas-objetos-de-conhecimento-e-habilidades',
                'http://basenacionalcomum.mec.gov.br/abase/medio',
                'http://basenacionalcomum.mec.gov.br/abase/o-ensino-medio-no-contexto-da-educacao-basica',
                'http://basenacionalcomum.mec.gov.br/abase/a-bncc-do-ensino-medio',
                'http://basenacionalcomum.mec.gov.br/abase/curriculos-bncc-e-itinerarios',
                'http://basenacionalcomum.mec.gov.br/abase/a-area-de-linguagens-e-suas-tecnologias',
                'http://basenacionalcomum.mec.gov.br/abase/competencias-especificas-de-linguagens-e-suas-tecnologias-para-o-ensino-medio',
                'http://basenacionalcomum.mec.gov.br/abase/a-area-de-linguagens-e-suas-tecnologias-no-ensino-medio-competencias-especificas-e-habilidades',
                'http://basenacionalcomum.mec.gov.br/abase/lingua-portuguesa',
                'http://basenacionalcomum.mec.gov.br/abase/lingua-portuguesa-no-ensino-medio-campos-de-atuacao-social-competencias-especificas-e-habilidades',
                'http://basenacionalcomum.mec.gov.br/abase/a-area-de-matematica-e-suas-tecnologias',
                'http://basenacionalcomum.mec.gov.br/abase/competencias-especificas-de-matematica-e-suas-tecnologias-para-o-ensino-medio',
                'http://basenacionalcomum.mec.gov.br/abase/matematica-e-suas-tecnologias-no-ensino-medio-competencias-especificas-e-habilidades',
                'http://basenacionalcomum.mec.gov.br/abase/consideracoes-sobre-a-organizacao-curricular',
                'http://basenacionalcomum.mec.gov.br/abase/a-area-de-ciencias-da-natureza-e-suas-tecnologias',
                'http://basenacionalcomum.mec.gov.br/abase/competencias-especificas-de-ciencias-da-natureza-e-suas-tecnologias-para-o-ensino-medio',
                'http://basenacionalcomum.mec.gov.br/abase/ciencias-da-natueza-e-suas-tecnologias-no-ensino-medio-competencias-especificas-e-habilidades',
                'http://basenacionalcomum.mec.gov.br/abase/a-area-de-ciencias-humanas-e-sociais-aplicadas',
                'http://basenacionalcomum.mec.gov.br/abase/competencias-especificas-de-ciencias-humanas-e-sociais-aplicadas-para-o-ensino-medio',
                'http://basenacionalcomum.mec.gov.br/abase/ciencias-humanas-e-sociais-aplicadas-no-ensino-medio-competencias-especificas-e-habilidades',
                'http://basenacionalcomum.mec.gov.br/abase/introducao',
                'http://basenacionalcomum.mec.gov.br/abase/#infantil']
crawl(listapaginas,2)


