import socket
import threading

bind_ip = "0.0.0.0"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip, bind_port))

server.listen(5)

print("Listening on {0}.{1}".format(bind_ip, bind_port))

def handle_client(client_socket):
    request = client_socket.recv(1024)
    print("Received: {0}".format(request))
    client_socket.send("ACK!")
    client_socket.close()

while 1:
    (client, address) = server.accept()
    print("Accepted connection from {0}:{1}".format(address[0], address[1]))
    client_handler = threading.Thread(target = handle_client, args = (client, ))
    client_handler.start()
