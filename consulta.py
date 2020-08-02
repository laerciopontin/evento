import pymysql
import nltk
from googlesearch import *
import re 
import webbrowser

#realiza a busca das palavras informadas pelo usuário
def buscaMaisPalavras(consulta):
    listacampos = 'p1.idstring'
    listatabelas = ''
    listaclausulas = ''
    palavrasid = []
    
    
    
    palavras = separaPalavras(consulta).split(' ')
    numerotabela = 1
    for palavra in palavras:
        if palavra != '':
            idpalavra = getIdPalavra(palavra)
            if idpalavra > 0:
                palavrasid.append(idpalavra)
                if numerotabela > 1:
                    listatabelas += ', '
                    listaclausulas += ' and '
                    listaclausulas += 'p%d.idstring = p%d.idstring and ' % (numerotabela - 1, numerotabela)
                listacampos += ', p%d.localizacao' % numerotabela
                listatabelas += 'palavra_localizacao p%d' % numerotabela
                listaclausulas += 'p%d.idpalavra = %d' % (numerotabela, idpalavra)
                numerotabela += 1
    consultacompleta = 'select %s from %s where %s' % (listacampos, listatabelas, listaclausulas)
    
    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice')
    cursor = conexao.cursor()
    cursor.execute(consultacompleta)
    linhas = [linha for linha in cursor]
    
    cursor.close()
    conexao.close()
    return linhas, palavrasid

def separaPalavras(texto):    
    stop = nltk.corpus.stopwords.words('portuguese')
    #biblioteca com lista de palavras ditas stopwords     
    splitter = re.compile('\\W+')
    #pega apenas palavras, retirando caracteres que não sejam (diminui a numerosidade)    
    palavras = ''
    lista = [p for p in splitter.split(texto) if p != ' ']
    #percorre todas as palavras de um texto e quebra as palavras desconsiderando os espaços vazios !=' '
    for p in lista:
        if p.lower() not in stop:
        #não insere na lista palavras ditas stopwords
            if len(p) > 1:
            #retira palavras com 1 caracter    
                palavras = palavras + ' ' + p.lower()
                #carrega os radicais da palavras na lista 
    return palavras


#busca a palavra pelo ser radical
def getIdPalavra(palavra):
    retorno = -1
    stemmer = nltk.stem.RSLPStemmer()
    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice')
    cursor = conexao.cursor()
    cursor.execute('select idpalavra from palavras where palavra = %s', stemmer.stem(palavra))
    if cursor.rowcount > 0:
        retorno = cursor.fetchone()[0]
    cursor.close()
    conexao.close()
    return retorno

#função para verificar quantidade de vezes que a palavra aparece no 'texto' (calculo de frequencia)
def frequenciaScore(linhas):
    contagem = dict([linha[0],0] for linha in linhas)
    for linha in linhas:
        contagem[linha[0]]+=1
    return normalizaMaior(contagem)

#seleciona strings que possui palavras informada pelo usuário     
def getString(idstring):
    retorno = ''
    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice')
    cursor = conexao.cursor()
    cursor.execute('select string from strings where idstring = %s', idstring)
    if cursor.rowcount > 0:
        retorno = cursor.fetchone()[0]
    
    cursor.close()
    conexao.close()
    return retorno

#identifica se a palavra esta mais próximo do inicio do 'texto de comparação' quando mais próximo, mais relevante (calculo de posicionamento 'inicio do texto')
def localizacaoScore(linhas):
    localizacoes = dict([linha[0], 1000000000] for linha in linhas)
    for linha in linhas:
        soma = sum(linha[1:])
        if soma < localizacoes[linha[0]]:
            localizacoes[linha[0]] = soma
    return  normalizaMenor(localizacoes)

#verifica distancia entre as palavras buscadas pelo usuário (calculo da distancia entre palavras)
def distanciaScore(linhas):
    if len(linhas[0])<=2:
        return normalizaMenor(dict([(linha[0], 1) for linha in linhas]))
    distancias = dict([(linha[0], 1000000) for linha in linhas])
    for linha in linhas:
        dist = sum([abs(linha[i]-linha[i-1]) for i in range(2, len(linha))])
        if dist < distancias[linha[0]]:
            distancias[linha[0]] = dist
    return normalizaMenor(distancias)
    

def contagemLinksScore(linhas):
    contagem = dict([linha[0], 1.0] for linha in linhas)
    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice')
    cursor = conexao.cursor()
    for i in contagem:
        cursor.execute('select count(*) from string_ligacao where idstring_destino = %s', i)
        contagem[i] = cursor.fetchone()[0]
    cursor.close()
    conexao.close()
    return normalizaMenor(contagem)


def textoLinkScore(linhas, palavrasid):
    contagem = dict([linha[0], 0] for linha in linhas)
    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice')
    for id in palavrasid:
        cursor = conexao.cursor()
        cursor.execute('select ul.idstring_origem, ul.idstring_destino from string_palavra up inner join string_ligacao ul on up.idstring_ligacao = ul.idstring_ligacao where up.idpalavra = %s',id)
      
    cursor.close()
    conexao.close()
    return contagem
    
def normalizaMaior(notas):
   try:
       menor = 0.00001
       maximo = max(notas.values())
       #evita erro de divisão por 0 zero
       if maximo == 0:
           maximo = menor
       return dict([(id, float(nota)/maximo) for (id, nota) in notas.items()])
   except :
        return ''

def normalizaMenor(notas):
    menor = 0.1
    minimo = min(notas.values())
    if minimo == 0:
        minimo = menor
    return dict([(id, float(minimo) / max(menor,nota)) for (id, nota) in notas.items()])
    
def pesquisaPeso(consulta):
    linhas , palavrasId = buscaMaisPalavras(consulta)
    totalScores = dict([linha[0], 0] for linha in linhas)    
    if frequenciaScore(linhas) == '':
        consulta = consulta+" no ensino fundamental sem anuncio"
    else:
        pesos = [(1.0, frequenciaScore(linhas)),
                 (1.0, localizacaoScore(linhas)),
                 (1.0, distanciaScore(linhas)),
                # (1.0, contagemLinksScore(linhas)),
                 #(1.0, textoLinkScore(linhas, palavrasId))
                 ]
        for(peso, scores) in pesos:
            for string in totalScores:
                totalScores[string] +=peso*scores[string]
        
        scoreordenado = sorted([(score, string) for (string,score) in totalScores.items()], reverse = 1)
        for(score, idstring) in scoreordenado:
            #print('%f\t%s' % (score, getString(idstring)))
            return getString(idstring)
    print(consulta)    
    return consulta

#to search, will ask search query at the time of execution
query = input("O que quer buscar? ")
#iexplorer_path = r'C:\Program Files (x86)Como foi o surgimento das primeiras civilizações\Internet Explorer\iexplore.exe %s'
chrome_path = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe %s'
for url in search(query, tld="co.in", num=1, stop = 1, pause = 2):
    print('A String ideal segundo BNCC é: ' + str(pesquisaPeso(query)))
    webbrowser.open("https://google.com/search?q=%s" % pesquisaPeso(query))   


#rank de quantidade de vezes que as palavras innformada pelo usuário aparecem na pesquisa e qual string deve ser utilizada
#def pesquisa(consulta):
##    linhas, palavrasid = buscaMaisPalavras(consulta)
#    #scores = dict([linha[0],0] for linha in linhas)
#    #scores = frequenciaScore(linhas)
#    #scores = localizacaoScore(linhas)
#    scores = distanciaScore(linhas)
#    #scores = contagemLinksScore(linhas)
#    #scores = textoLinkScore(linhas, palavrasid)
#    scoreordenado = sorted([(score, string) for (string,score) in scores.items()], reverse = 1)
#    for(score, idstring) in scoreordenado:
#        print('%f\t%s' % (score, getString(idstring)))
#        
#pesquisaPeso('como somar')

#def buscaUmaPalavra(palavra):
#    idPalavra = getIdPalavra(palavra)
#    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice')
#    cursor = conexao.cursor()
#    cursor.execute('select strings.string from palavra_localizacao plc inner join strings on plc.idstring = strings.idstring where plc.idpalavra = %s', idPalavra)
#    paginas = set()
#    for string in cursor:
##        paginas.add(string[0])
#    
#    print('Páginas encontradas: '+str(len(paginas)))
#    for string in paginas:
#        print(string)
#    cursor.close()
#    conexao.close()
    
#buscaUmaPalavra('Soma')
