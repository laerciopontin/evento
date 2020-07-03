oimport os
import numpy as np
import win32com.client as win32
import nltk
#nltk.download()
import pymysql
import re 
from unicodedata import normalize


# Função para abrir arquivo Excel
excel = win32.gencache.EnsureDispatch('Excel.Application')
def abreWorkbook(xlArquivo):
	global excel
	global win32
	try:        
	    xlwb = win32.GetObject(xlArquivo)            
	except Exception as e:
	    try:
	        xlwb = excel.Workbooks.Open(xlArquivo)
	    except Exception as e:
	        print(e)
	        xlwb = None                    
	return(xlwb)   
    
def inserePalavraLocalizacao(idstring, idpalavra, localizacao):
    #função para inserir localizacao da palavra
    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice', autocommit = True, use_unicode = True, charset = 'utf8mb4')
    cursor = conexao.cursor()
    print('insert into palavra_localizacao (idstring, idpalavra, localizacao) values ( ' + str(idstring)+', ' + str(idpalavra)+ ', ' + str(localizacao)+')')
    cursor.execute('insert into palavra_localizacao (idstring, idpalavra, localizacao) values (%s, %s, %s)', (idstring, idpalavra, localizacao))
    idpalavralocalizacao = cursor.lastrowid
    cursor.close()
    conexao.close()
    return idpalavralocalizacao

def palavraIndexada(palavra):
    #verifica se já existe a palavra na base
    retorno = -1 #não existe a palavra na base
    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice')
    cursor = conexao.cursor()
    print('select idpalavra from palavras where palavra = ' + str(palavra))
    cursor.execute('select idpalavra from palavras where palavra = %s', str(palavra))
    if cursor.rowcount > 0:
        retorno = cursor.fetchone()[0] #já existe a palavra na base
    print(retorno)
    cursor.close()
    conexao.close()
    return retorno

def inserePalavra(palavra):
    #função para inserir nova palavra
    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice', autocommit = True, use_unicode = True, charset = 'utf8mb4')
    cursor = conexao.cursor()
    print('insert into palavras (palavra) values (' + str(palavra)+')')
    cursor.execute('insert into palavras (palavra) values (%s)', str(palavra))
    idpalavra = cursor.lastrowid
    cursor.close()
    conexao.close()
    return idpalavra
    
def paginaIndexada(string):
    #função para buscar página indexada
    retorno = -1 #não existe a página
    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice', use_unicode = True, charset = 'utf8mb4')
    cursorString = conexao.cursor()
    cursorString.execute('select idstring from strings where string = %s', string)
    if cursorString.rowcount > 0 :
        #print("String cadastrada!")
        idstring = cursorString.fetchone()[0]
        cursorPalavra = conexao.cursor()
        cursorPalavra.execute('select idstring from palavra_localizacao where idstring = %s', str(idstring))
        if cursorPalavra.rowcount > 0:
           retorno = -2 #existe a página com palavras cadastradas 
        else:            
           retorno = -2 #existe a página sem palavras cadastradas
        cursorPalavra.close()
    cursorString.close()
    conexao.close()
    return retorno
    
def inserePagina(string):
    #função para indexar nova página
    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice', autocommit = True, use_unicode = True, charset = 'utf8mb4')
    cursor = conexao.cursor()
    print('insert into strings (string) values (' + str(string)+')')
    cursor.execute('insert into strings (string) values ( %s )', str(string).lower())
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

#teste = separaPalavras('Teste aleatório, para restar a classificação, obrigado! 01/01/2020')

def getText(sopa):
    ##função para remover tags html e js
    for tags in sopa(['script', 'style']):
        tags.decompose()
    return ' '.join(sopa.stripped_strings)
    ##remove espaços em branco entre strings

def indexador(string, sopa):
    
    #verifica e insere valores na base de dados
    indexada = paginaIndexada(string)
    #verifica se existe a página no banco e processa
    if indexada == -2:
        print('String já cadastrada')
        return
    elif indexada == -1:
        idnovaPagina = inserePagina(string)
    elif indexada > 0:
        idnovaPagina = indexada
        
    print('Indexando ' + string)
    
    #texto = getText(sopa)
    palavras = separaPalavras(sopa)
    
    for i in range(len(palavras)):
        #verifica se existe a palavra na base e processa
        palavra = palavras[i]
        idPalavra = palavraIndexada(palavra)
        if idPalavra == -1:
            idPalavra = inserePalavra(palavra)
        print(' '+str(idnovaPagina)+' '+str(idPalavra)+' '+str(i))    
        inserePalavraLocalizacao(idnovaPagina, idPalavra, i)
        #insere a localização da palavra


def insereStringLigacao(idstring_origem, idstring_destino):
    #função de relacionamento entre strings relacionadas (com mesmas palavras)
    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice', autocommit = True, use_unicode = True, charset = 'utf8mb4')
    cursor = conexao.cursor()
    print('insert into string_ligacao (idstring_origem, idstring_destino) values'+ str(idstring_origem) + str(idstring_destino)+')')
    cursor.execute('insert into string_ligacao (idstring_origem, idstring_destino) values (%s, %s)', (idstring_origem, idstring_destino))
    idstring_ligacao = cursor.lastrowid
    cursor.close()
    conexao.close()
    return idstring_ligacao


def insereStringPalavra(idpalavra, idstring_ligacao):
    #função de relacionamento as palavras pertencentes as strings
    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice', autocommit = True, use_unicode = True, charset = 'utf8mb4')
    cursor = conexao.cursor()
    print('insert into string_palavra (idpalavra, idstring_ligacao) values ('+ str(idpalavra) + str( idstring_ligacao)+')')
    cursor.execute('insert into string_palavra (idpalavra, idstring_ligacao) values (%s, %s)', (idpalavra, idstring_ligacao))
    idstring_palavra = cursor.lastrowid
    cursor.close()
    conexao.close()
    return idstring_palavra
 
def getIdStringLigacao(idstring_origem, idstring_destino):
    idstring_ligacao = -1
    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice', autocommit = True, use_unicode = True, charset = 'utf8mb4')
    cursor = conexao.cursor()
    #print('insert into string_ligacao (idstring_origem, idstring_destino) values (%s, %s)', (idstring_origem, idstring_destino)+')')
    cursor.execute('select idstring_ligacao from string_ligacao where idstring_origem = %s and idstring_destino = %s', (idstring_origem, idstring_destino))
    if cursor.rowcount >0:
        idstring_ligacao = cursor.fetchone()[0]
    cursor.close()
    conexao.close()
    return idstring_ligacao

def getIdString(string):
    idstring = -1 #não existe a página
    conexao = pymysql.connect(host='localhost', user='root', passwd='laercio01', db='indice', use_unicode = True, charset = 'utf8mb4')
    cursorString = conexao.cursor()
    cursorString.execute('select idstring from strings where string = %s', string)
    if cursorString.rowcount > 0 :
        #print("String cadastrada!")
        idstring = cursorString.fetchone()[0]
        
    cursorString.close()
    conexao.close()
    return idstring       

def stringLigaPalavra(string_origem, string_destino):
    palavras = separaPalavras(string_destino)
    idstring_origem = getIdString(string_origem)
    idstring_destino = getIdString(string_destino)    
    if idstring_destino == -1:
        idstring_destino = inserePagina(string_destino)
    
    if idstring_origem == idstring_destino:
        return
    
    if getIdStringLigacao(idstring_origem, idstring_destino)>0:
        return
    
    idstring_ligacao = insereStringLigacao(idstring_origem, idstring_destino)
    
    for palavra in palavras:
        idpalavra = palavraIndexada(palavra)
        if idpalavra == -1:
            idpalavra = inserePalavra(palavra)    
        insereStringPalavra(idpalavra, idstring_ligacao)
        
def removerAcentos(txt):
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')
   
# Nome das abas da planilha e suas respectivas quantidades de linhas
distribuicaoPlanilha = [['linguaPortuguesa',391],['arte', 61],['educacaoFisica', 69], 
                        ['linguaInglesa',88],['matematica',247],['ciencia',111],['geografia',123],
                        ['historia',151],['ensinoReligioso',63]]

# Abrir arquivo e planilha
wb = abreWorkbook(os.getcwd()+'/bncc.xlsx')

#Percorre abas das planilhas e executa a inserção dos dados ne banco
for aba in range(0,len(distribuicaoPlanilha)):
    #Recebe nome e tamanho da próxima planilha a ser varrifa
    materia = distribuicaoPlanilha[aba]
    planilha =  wb.Worksheets(materia[0])
    
    #Percorre toadas as linhas da aba, realizando a leitura e inserção dos valores textuais a serem minerados
    for linha in range(1,materia[1]):
        # Selecionar dados colunas B e D, que compõem a String aprimorada
        colunasstring =  "B" + str(linha) + ":D" + str(linha)
        # Selecionar dados colunas C e G, que compõem o texto a ser minerado
        colunassopa = "C" + str(linha) + ":G" + str(linha)
        #Une as colunas de B a D a ser inserida no banco como String Aprimorada
        stringideal = np.array(planilha.Range(colunasstring).Value)
        sopa = np.array(planilha.Range(colunassopa).Value)
        #Une as colunas de C a G a ser inserida no banco como texto minerado
        stringideal = stringideal.item(0)+' '+stringideal.item(1)+' '+stringideal.item(2)
        sopa = str(sopa.item(0))+' '+str(sopa.item(1))+' '+str(sopa.item(2))
        #Função que analisa o texto, realiza o pré-processamento textual e insere no banco, 
        # relacionando a String aprimorada e o texto relacionado
        indexador(stringideal, sopa)

        