import sys
import socket
HOST=''
PORT=8000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)
while True:
        new_connection, add = s.accept()
        while True:
            data = new_connection.recv(4096)
            if data == bytes('exit', 'utf-8'):
                try:
                    new_connection.shutdown(1)
                finally:
                    new_connection.close()
                    sys.exit(0)
            elif data:
                new_connection.send(data)