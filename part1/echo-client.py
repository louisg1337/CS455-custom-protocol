import socket

# HOST = input("IP Address: ")
# PORT = int(input("Host: "))
HOST = '127.0.0.1'
PORT = 65432

print("PORT: " + str(PORT))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.sendall(b"Hello, world")
data = s.recv(1024)
print(f"Received {data!r}")
