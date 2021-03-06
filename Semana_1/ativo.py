import socket
HOST = '127.0.0.1'
PORT = 8000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST, PORT)
s.connect(dest)
while True:
    data = input()
    res = bytes(data, 'utf-8') 
    s.send(res)
    if(data == 'exit'):
        break
    echo = s.recv(4096)
    if echo:
        print("Echo server returned: " + echo.decode("utf-8"))

s.close()