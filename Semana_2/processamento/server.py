import sys
import os
sys.path.append(os.getcwd()+"/Semana_2/dados")
import socket
import re
import string
from data import openFile
HOST=''
PORT=8000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)
while True:
    new_connection, add = s.accept()
    while True:
        try:
            data = new_connection.recv(4096)
            # testando se o cliente fechou a conexao
            if not data:
                new_connection.close()
                break
            else:
                data = data.decode("utf-8")
                data = data.split(",")
                r=""
                # percorrendo a possivel lista de arquivos
                for d in data:
                    dicio = {}
                    d = d.strip(" ")
                    if d:
                        r+=d+":\n"
                        try:
                            # solicitando da camada de dados o conteudo o arquivo
                            arq = openFile(os.getcwd()+"/"+d)
                        except Exception:
                            r+=f"\tO arquivo {d} não foi encontrado\n"
                            continue
                        arq = arq.split("\n")
                        for linha in arq:
                            if linha:
                                linha = linha.lower()
                                linha = linha.strip(" ")
                                linha = linha.strip("\n")
                                linha = re.compile('[%s]' % re.escape(string.punctuation)).sub("",linha)
                                palavras = linha.split(" ")
                                for p in palavras:
                                    if p:
                                        if p in list(dicio):
                                            dicio[p] = dicio[p] + 1
                                        else:
                                            dicio[p] = 1
                        dicio=sorted(dicio.items(),  key=lambda x: x[1], reverse=True)
                        # montando a resposta para o cliente
                        for i, k in zip(range(0,10),dicio):
                            r += "\t"+k[0]+": "+str(k[1])+"\n"
                        r+="\n"
                new_connection.send(bytes(r, 'utf-8'))
        except:
            # caso aconteça algum erro, o servidor comunica o problema pede novamente o arquivo
            new_connection.send(bytes("Tivemos algum problema, tente novamente", 'utf-8'))