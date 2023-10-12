import socket

# Prompt user for IP and Port
HOST = input("IP Address: ")
PORT = int(input("Port: "))

# Variable instantiations the set up the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))

# Listen for connection by client
s.listen()
conn, addr = s.accept()
print(f"Connected by {addr}")

# Listen for data send by server, then echo it back
while True:
    data = conn.recv(1024)
    if not data:
        break
    conn.sendall(data)