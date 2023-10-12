import socket

# Prompt user for IP and Port
HOST = input("IP Address: ")
PORT = int(input("Port: "))

# Setup socket and attempt to connect to server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

# Send out message
s.sendall(b"Hello, world")

# Receive message back, decode it, and print it
data = s.recv(1024).decode("utf-8")
print(f"Received {data!r}")
