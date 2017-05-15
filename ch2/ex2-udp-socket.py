import socket

target_host = "www.google.com"
target_port = 80

# set up UDP client (SOCK_DGRAM makes it use UDP datagrams)
# doesn't need to connect (b/c not TCP)
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client.sendto("GET / HTTP/1.1\nHost: google.com\n\n",
              (target_host, target_port))

(data, address) = client.recvfrom(4096)

print(data)
