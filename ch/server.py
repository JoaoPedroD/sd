import sys
from collections import OrderedDict
import os
import socketserver
import multiprocessing
import socket
import time
import hashlib
 
# porta de escuta do servidor de echo
PORTA = 10001
HOST  = 'localhost'

class No():
    def __init__(self,ID, porta):
        self.prox   = None
        self.finger = {}
        self.id     = ID
        self.tab    = {}
        self.porta  = porta
        self.sock   = None
        self.escuta()

    def escuta(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.porta))
        self.sock.listen(2)
        # print(f"PORTA = {self.porta}")
        while True:
            new_connection, _ = self.sock.accept()
            data = new_connection.recv(2*4096)
            if not data:
                new_connection.close()
                continue
            data = data.decode("utf-8")
            data=data.split(',')
            dicio = {}
            for i in data:
                dic = i.split(':')
                # print(f"dic = {dic}")
                dicio[dic[0].strip()]=dic[1].strip()
            # print(dicio)
            self.atende(dicio)
            new_connection.close()

    def setProximo(self,porta,finger=None):
        self.prox=porta
        if finger:
            self.setFinger(finger)
        # print(f"PORTA ATUAL = {self.porta} SETANDO O PROXIMO {self.prox}")
    
    def setFinger(self,fingers):
        if fingers:
            fingers=fingers.replace("[","")
            fingers=fingers.replace("]","")
            fingers=fingers.split(';')
            # print(f"fingers = { fingers }")
            n = 0
            for i in fingers:
                # print(f"finger = {i}")
                self.finger[(2**n)]=int(i.strip())
                n+=1

    def insere(self,noOrigem, chave, valor, tam):
        # print(f"INSERE origem = {noOrigem} chave = {chave}, valor = {valor}, tamanho = {tam}")
        # no = int(len(chave))%int(tam)
        result = hashlib.sha1(chave.encode()).hexdigest()
        # print(f"len(result) = {len(result)}")
        no = int(result, 36) % int(tam)
        # print(int(result, 16) % int(tam))
        # print(f"no = {no}")
        # print(f"self.id = {self.id}")
        # print(f"self.finger = {self.finger}")
        salto=None
        dest=None
        if no != self.id:
            if self.finger:
                for i in range(0,len(self.finger)):
                    if (self.id + (2**i)) == no:
                        salto=i
                        break
                    elif (self.id + (2**i)) < no:
                        salto=i
                if salto == None:
                    salto=len(self.finger)-1
                # print(f"2**salto = {2**salto}")
                dest = (HOST, self.finger[2**salto])
            else:
                dest = (HOST, self.prox)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(dest)
            args = f"func: insere, origem: {self.id}, k: {chave}, v: {valor}, tam: {tam}"
            s.sendall(bytes(args, 'utf-8'))
        else:
            # print(f"#####INSERE: ENCONTREI O NO {self.id} == {no}")
            self.tab[chave]=valor

    def busca(self,noOrigem, chave, tam):
        result = hashlib.sha1(chave.encode()).hexdigest()
        no = int(result, 16) % int(tam)
        salto=None
        dest=None
        if no != self.id:
            if self.finger:
                for i in range(0,len(self.finger)):
                    if (self.id + (2**i)) == no:
                        salto=i
                        break
                    elif (self.id + (2**i)) < no:
                        salto=i
                if salto == None:
                    salto=len(self.finger)-1
                # print(f"2**salto = {2**salto}")
                dest = (HOST, self.finger[2**salto])
            else:
                dest = (HOST, self.prox)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(dest)
            args = f"func: busca, origem: {self.id}, k: {chave}, tam: {tam}"
            s.sendall(bytes(args, 'utf-8'))
            s.close()
        else:
            # print(f"#####BUSCA: ENCONTREI O NO {self.id} == {no}")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dest = (HOST, 10002)
            s.connect(dest)
            args = None
            if chave in self.tab:
                args = f"no = {self.id}\n{chave} = {self.tab[chave]}"
                # print(args)
            else:
                args = f"A chave {chave} não foi encontrada"
                # print(args)
            s.sendall(bytes(args, 'utf-8'))
            s.close()

    def atende(self,args):
        func = args['func']
        # print(f'ATENDE = {func}')
        if func=='create':
            self.create()
        elif func == 'join':
            self.join()
        elif func == 'setProximo':
            if 'f' in args:
                f=args['f']
                # print(f'ATENDE args[\'f\'] = {f}')
                self.setProximo(int(args['porta']),args['f'])
            else:
                self.setProximo(int(args['porta']))
        elif func == 'insere':
            self.insere(int(args['origem']), args['k'], args['v'], args['tam'])
        elif func == 'busca':
            self.busca(int(args['origem']), args['k'], args['tam'])

    def create(self):
        print("create")

    def join(self):
        print("join")


class Anel():
    def __init__(self, quant):
        self.noDict     = OrderedDict()
        self.num_node   = num
        self.item_keys  = set()
    
    def add_node(self, quant):
        # porta=50000
        for i in range(0,2**quant):
            porta_livre=None
            with socketserver.TCPServer(("localhost", 0), None) as s:
                porta_livre = s.server_address[1]
            cliente = multiprocessing.Process(target=No, args=(i,porta_livre))
            cliente.start()
            time.sleep(1)
            
            # no = No(i)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dest = (HOST, porta_livre)
            s.connect(dest)
            if len(self.noDict) == 0:
                # print("create")
                # s.sendall(bytes(args, 'utf-8'))
                args = f"func: create"
                tam = len(args)
                enviado=0
                while tam > enviado:
                    enviado+=s.send(bytes(args[enviado:], 'utf-8'))
            else:
                # print("join")
                args = f"func: join, join: {i}"
                s.sendall(bytes(args, 'utf-8'))
            self.noDict[i] = porta_livre
        # print(f"self.noDict = {self.noDict}")
        for i in range(0,len(self.noDict)):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dest = (HOST, self.noDict[i])
            s.connect(dest)
            args=None
            if (i+1)%len(self.noDict) in self.noDict:
            # if i+1 in self.noDict:
                args = f"func: setProximo, porta: {self.noDict[(i+1)%len(self.noDict)]}, f: ["
                # args = f"func: setProximo, porta: {self.noDict[i+1]}, f: ["
            entrei=False
            for j in range(0,len(self.noDict)):
                # print(f"(i+(2**j))%len(self.noDict) = {(i+(2**j))%len(self.noDict)}")
                no = (i+(2**j))%len(self.noDict)
                if no in self.noDict and no != i:
                    args=args+str(self.noDict[int(no)])+";"
                    entrei=True
                else:
                    if entrei:
                        entrei=False
                        args=args[:-1]
                        args=args+"]"
                        break
            # print(f"args = {args}")
            if not args:
                args=f"func: setProximo, porta: {self.noDict[0]}"
            s.sendall(bytes(args, 'utf-8'))
            s.close()
    
    def insere(self,no,k,v):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dest = (HOST, self.noDict[no])
        s.connect(dest)
        args = f"func: insere, origem: {no}, k: {k}, v: {v}, tam: {len(self.noDict)}"
        tam = len(args)
        enviado=0
        while tam > enviado:
            enviado+=s.send(bytes(args[enviado:], 'utf-8'))
    
    def busca(self,no,chave):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dest = (HOST, self.noDict[no])
        s.connect(dest)
        args = f"func: busca, origem: {no}, k: {chave}, tam: {len(self.noDict)}"
        s.sendall(bytes(args, 'utf-8'))

# dispara o servidor
if __name__ == "__main__":
    num = input("Digite a quantidade de nos:")
    anel = Anel(int(num))
    anel.add_node(int(num))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', PORTA))
    s.listen(2)
    while True:
        new_connection, _ = s.accept()
        data = new_connection.recv(2*4096)
        if not data:
            new_connection.close()
            continue
        data = data.decode("utf-8")
        data=data.strip()
        # print(f"data = {data}")
        if 'busca' in data:
            # print("busca")
            data=data.replace("busca","")
            data=data.replace("(","")
            data=data.replace(")","")
            data=data.split(",")
            # print(f"data {data}")
            if len(data) == 2:
                noOrigem=data[0]
                chave=data[1]
                # print(f"noOrigem = {noOrigem} chave = {chave}")
                if noOrigem and chave:
                    anel.busca(int(noOrigem),chave)
                else:
                    print("Faltou alguma informacao para a busca")
            else:
                print("Faltou alguma informacao para a busca")
        elif 'insere' in data:
            # print("insere")
            data=data.replace("insere","")
            data=data.replace("(","")
            data=data.replace(")","")
            data=data.split(",")
            # print(f"data {data}")
            if len(data) == 3:
                noOrigem=data[0]
                chave=data[1]
                valor=data[2]
                # print(f"noOrigem = {noOrigem} chave = {chave} valor = {valor} ")
                if noOrigem and chave and valor:
                    anel.insere(int(noOrigem),chave,valor)
                else:
                    print("Faltou alguma informacao para a funcao de inserção")
            else:
                print("Faltou alguma informacao para a funcao de inserção")
        # print(dicio)
        new_connection.close()
    sys.exit()
