import socket
import select, time
import threading
import sys, errno

lock = threading.Lock()
PORTAS=[10000,10001,10002,10003]
LOCAL='localhost'

def checkPort(port):
    # print(f"port = {port}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    try:
        sock.bind(('',int(port)))
    except: #socket.error as e:
        # if e.errno == 57:
        #     return False
        return False
    sock.close()
    return True
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # return True if s.connect_ex((LOCAL, int(port))) == 0 else False

class RBCP():
    def __init__(self,id):
        self.X=0
        self.id=id
        self.power= 0
        self.hist=[]
        self.avaiable=True
        self.calledable=True
        # time.sleep(0.3)
        if id < 2:
            self.power=1
        # print(f"self.X = {self.X}")
        # print(f"self.id = {self.id}")
    
    def print(self):
        print(f"self.id = {self.id}\nself.X = {self.X}\nself.power = {self.power}")
    
    def histo(self):
        print(f"Historico = {self.hist}\n")

    def printX(self):
        print(f"X = {self.X}\n")

    def mudarX(self,x):
        # print(f"{self.power} = {self.id}")
        if(self.id==self.power):
            lock.acquire()
            self.X=x
            self.hist.append((PORTAS.index(int(PORTAS[self.id-1]))+1,self.X))
            lock.release()
            self.avisaMud()
        else:
            self.pedirLideranca()
    
    def escuta(self):
        conf={10000:0,10001:0,10002:0,10003:0}
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(('',int(PORTAS[self.id-1])))
        if self.power==0:
            self.pegaLider()
            self.pegaX()
        while True:
            # t = threading.Timer(2.0, self.task)
            m,a=sock.recvfrom(1024)
            m=m.decode('utf-8')
            m=m.split(":")
            # print(f'm[0] = {m[0]}')
            if m[1]=='5':
                msg="5:"+str(self.power==self.id)+":"+str(self.X)
                # print(f"msg = {msg}\nint(m[0]) = {int(m[0])}")
                enviado=0
                tam = len(msg)
                while tam > enviado:
                    enviado+=sock.sendto((msg[enviado:]).encode('utf-8'),('localhost', int(m[0])))
                # print("ENVIEI")
            elif m[0] == '5':
                # print(f"ENTREI 5 m[1] = {m[1]}")
                if m[1] == "True":
                    # print(f"a[1] = {a[1]}")
                    self.power=PORTAS.index(int(a[1]))+1
                    self.X=int(m[2])
                    # print(f"PORTAS.index(int(a[1])) = {PORTAS.index(int(a[1]))}")
            elif m[0] == '6':
                # print(f"ENTREI 6")
                # lock.acquire()
                if m[3]=='0':
                    # print(a)
                    self.X=int(m[2])
                    self.hist.append((PORTAS.index(int(m[1]))+1,self.X))
                    self.sendConfirm(int(m[1]))
                else:
                    if self.hist[len(self.hist)-1] == (PORTAS.index(int(m[1]))+1,self.X):
                        self.sendConfirm(int(m[1]))
                    else:
                        self.X=int(m[2])
                        self.hist.append((PORTAS.index(int(m[1]))+1,self.X))
                        self.sendConfirm(int(m[1]))
                # lock.release()
                
            elif m[0] == '7':
                # print('ENTREI 7')
                # print(m)
                if self.avaiable:
                    lock.acquire()
                    # print('PASSEI')
                    self.power=PORTAS.index(int(m[1]))+1
                    self.enviaBroad("9:"+str(self.power))
                    lock.release()
            elif m[0] == '8':
                # print("ENTREI 8")
                break
            elif m[0] == '9':
                lock.acquire()
                self.power=int(m[1])
                lock.release()
            elif m[0] == '10':
                lock.acquire()
                conf[int(m[1])]=conf[int(m[1])]+1
                # print(f'confirma = {conf}')
                lock.release()
                if self.calledable:
                    self.calledable=False
                    t = threading.Timer(2.0, self.task,[conf])
                    t.start()



    def task(self,c):
        # print(f'TASK = {c}')
        l=c[int(PORTAS[self.id])]
        for i in list(c.keys()):
            if int(i) != int(PORTAS[self.id-1]):
                if l == c[int(i)]:
                    # print("TRUE")
                    continue
                elif l < c[int(i)]:
                    self.reEnvia(int(PORTAS[self.id]))
                else:
                    self.reEnvia(int(i))
        self.calledable=True

    def enviaBroad(self,msg):
        # print(f"msg = {msg}")
        self.avaiable=False
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        for i in PORTAS:
            # print(f" {int(PORTAS[self.id-1])} != {int(i)} = {int(PORTAS[self.id-1]) != int(i)}")
            if int(PORTAS[self.id-1]) != int(i):
                # print("ENVIEI")
                enviado=0
                tam = len(msg)
                while tam > enviado:
                    enviado+=s.sendto((msg[enviado:]).encode('utf-8'), ('localhost', int(i)))
        self.avaiable=True
    
    def pegaLider(self):
        self.enviaBroad(str(PORTAS[self.id-1])+":5")
    
    def pegaX(self):
        self.enviaBroad(str(PORTAS[self.id-1])+":5")

    def avisaMud(self):
        self.enviaBroad("6:"+str(PORTAS[self.id-1])+":"+str(self.X)+":0")

    def termina(self):
        # print("ENVIEI 8")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        msg="8:"
        enviado=0
        tam = len(msg)
        while tam > enviado:
            enviado+=s.sendto((msg[enviado:]).encode('utf-8'), ('localhost', int(PORTAS[self.id-1])))
    
    def pedirLideranca(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        msg="7:"+str(PORTAS[self.id-1])
        enviado=0
        tam = len(msg)
        while tam > enviado:
            enviado+=s.sendto((msg[enviado:]).encode('utf-8'), ('localhost', int(PORTAS[self.power-1])))

    def setAvaiable(self,b):
        self.avaiable=b

    def tenhoChapeu(self):
        return True if self.id==self.power else False

    def sendConfirm(self, porta):
        # print('send confirm')
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        msg="10:"+str(PORTAS[self.id-1])
        enviado=0
        tam = len(msg)
        while tam > enviado:
            enviado+=s.sendto((msg[enviado:]).encode('utf-8'), ('localhost', int(porta)))
    
    def reEnvia(self, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        msg="6:"+str(PORTAS[self.id-1])+":"+str(self.X)+":1"
        enviado=0
        tam = len(msg)
        while tam > enviado:
            enviado+=s.sendto((msg[enviado:]).encode('utf-8'), ('localhost', int(port)))

if __name__ == "__main__":
    A=None
    # entradas = [sys.stdin]
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    for i in range(0,len(PORTAS)):
        # print(f"checkPort(PORTAS[i]) = {checkPort(PORTAS[i])}")
        if checkPort(PORTAS[i]):
            # print(f"Port is open i = {i}")
            # print(f"id = {1+i}")
            A=RBCP(i+1)
            break
    # A.print()
    # sock.listen(1)
    cliente = threading.Thread(target=A.escuta)
    cliente.start()

    # entradas.append(sock)
    while True:
        # leitura, escrita, excecao = select.select(entradas, [], [])
        # for pronto in leitura:
            # if pronto == sys.stdin: #entrada padrao
        cmd = input("1. ler o valor atual de X na replica\n2. ler o historico de alterações do valor de X\n3. alterar o valor de X\n4. finalizar o programa\n")
        if cmd == '3':
            if A.tenhoChapeu():
                while True:
                    A.setAvaiable(False)
                    i = input("Qual novo valor de X?\n")
                    j = input("Gostaria de mudar o valor de  X [s]im, [n]ão\n")
                    if j == 'n':
                        A.mudarX(int(i))
                        break
                    elif j == 's':
                        A.hist.append((PORTAS.index(int(PORTAS[A.id-1]))+1,int(i)))
            else:
                print('Tentarei pegar o chapeu, tente novamente')
                A.pedirLideranca()
            A.setAvaiable(True)
        elif cmd == '2':
            A.histo()
            continue
        elif cmd == '1':
            A.printX()
        elif cmd == '4':
            A.termina()
            break
    sys.exit(0)
