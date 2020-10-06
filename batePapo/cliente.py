import sys
import socket
import threading

HOST = '127.0.0.1'
PORT = 8000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST, PORT)
s.connect(dest)
kill=False
def escuta():
    while True:
        try:
            mensagem = s.recv(4096)
            print(mensagem.decode("utf-8"))
        except:
            if kill:
                break
            print("DEU ALGUMA COISA ERRADA")


cliente = threading.Thread(target=escuta)
cliente.start()
while True:
    data = input()
    if data=="fim":
        kill=True
        break
    elif data:
        # print("ENTREI")
        tam = len(data)
        while tam >0:
            # print(tam)
            enviado = s.send(bytes(data, 'utf-8'))
            tam=tam-enviado
s.close()
sys.exit()