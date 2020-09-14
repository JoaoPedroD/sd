import sys
import socket
HOST = '127.0.0.1'
PORT = 8000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST, PORT)
s.connect(dest)
while True:
    data = input("Entre um arquivo ou uma lista de arquivos separado por virgula\nPara sair da aplicação aperte enter\n")
    if data:
        # enviando a mensage com os arquivos para o servidor
        res = bytes(data, 'utf-8')
        s.send(res)
        # # recebendo a mensage com os arquivos para o servidor
        echo = s.recv(4096)
        if echo:
            print(echo.decode("utf-8"))
    else:
        s.close()
        break
sys.exit()