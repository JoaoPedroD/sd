import sys
import socket
import threading
HOST = 'localhost'
# rodando=True

def threadDeResposta():
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    c.bind(('localhost', 10002))
    c.listen(1)
    while(True):
        # rodando
        # print(f"rodando = {rodando}")
        new_connection, _ = c.accept()
        data = new_connection.recv(2*4096)
        if not data:
            new_connection.close()
            continue
        data = data.decode("utf-8")
        print(data)
    c.close()
    # print("terminei")


cliente = threading.Thread(target=threadDeResposta)
cliente.start()
while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dest = (HOST, 10001)
    s.connect(dest)
    data = input("Entre com a funcao\n")
    # print(data)
    if data == "fim":
        # print("entrei no fim")
        # rodando=False
        break
    else:
        s.sendall(bytes(data, 'utf-8'))
        s.close()
        
sys.exit()