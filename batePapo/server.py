import socket 
import select 
import sys 
import threading

HOST = ""

PORT = 8000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

server.bind((HOST, PORT)) 

server.listen(10)

list_of_clients = [] 

lock = threading.Lock()

def threadDoCliente(conn, addr):

    conn.send(bytes("Bem vindo!", 'utf-8'))
    while True: 
        try: 
            message = conn.recv(4096) 
            if message: 
                mensageDecode = message.decode("utf-8")
                print("==" + addr[0] + "== " + mensageDecode)
                if mensageDecode == "lista":
                    mensagem=""
                    k=1
                    for i in list_of_clients:
                        if i != conn:
                            mensagem=mensagem+"Usuario "+str(k)+": "+str(i.getsockname()[0])+"\n"
                            k+=1
                        else:
                            mensagem=mensagem+"(Você)Usuario "+str(k)+": "+str(i.getsockname()[0])+"\n"
                            k+=1
                    # print("MENSAGEM = "+mensagem)
                    enviaMensagem(mensagem, conn, 1)
                # print("--" + addr[0] + "-- " + message.decode("utf-8"))
                else:
                    enviaMensagem(mensageDecode, conn, 2)
            else: 
                remove(conn) 

        except: 
            continue

def envia(message, conn):
    tam = len(message)
    while tam >0:
        enviado = conn.send(bytes(message, 'utf-8')) 
        tam=tam-enviado


def enviaMensagem(message, conn, flag):
    # print("ENTREI = " + message)
    if flag==1:
        try:
            lock.acquire()
            envia(message, conn)
            lock.release()
        except: 
            conn.close() 
            remove(conn) 
    elif flag==2:
        # print("message = " + message)
        dest = message.split(':', 1)[0].strip()
        # print("dest = " + dest)
        mens = message.split(':', 1)[1].strip()
        # print("mensagem = " + mens)
        k=1
        print(list_of_clients)
        for i in list_of_clients:
            if k == int(dest):
                lock.acquire()
                mens="==Usuario "+ str(k) +":" + str(i.getsockname()[0]) + "==\n    "+mens
                envia(mens,i)
                lock.release()
                break
            k+=1
        


def remove(c): 
    if c in list_of_clients: 
        lock.acquire()
        list_of_clients.remove(c)
        lock.release()

while True: 
    leitura, escrita, excecao = select.select([sys.stdin, server], [], [])

    for pronto in leitura:
        if pronto == server:

            conn, addr = server.accept() 

            list_of_clients.append(conn)

            print (addr[0] + " conectado")

            cliente = threading.Thread(target=threadDoCliente, args=(conn,addr))
            cliente.start()
        elif pronto == sys.stdin:
            cmd = input()
            if cmd == 'fim': #Para finalizar o servidor
                if not list_of_clients:
                    server.close()
                    sys.exit()
                print("Ainda existem conexões")

conn.close() 
server.close() 
