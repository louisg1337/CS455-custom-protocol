import socket
import time

HOST = "csa3.bu.edu"
PORT = 58069  

def CSP():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    print(f"Connected by {addr}")
    while True:
        data = conn.recv(1024)
        decodedData = data.decode('utf-8')
        parsedData = decodedData.split()
        
        # Handle termination sequence and faulty data
        if len(parsedData) < 5:
            if len(parsedData) == 1 and parsedData[0] == 't':
                conn.sendall("200 OK: Closing Connection".encode('utf-8'))
            else:
                conn.sendall("404 ERROR: Invalid Connection Setup Message".encode('utf-8'))
            break    
            
        # Put parse data to variable name
        protocolPhase = parsedData[0]
        measurementType = parsedData[1]
        numProbes = parsedData[2]
        messageSize = parsedData[3]
        serverDelay = parsedData[4]
        
        # Check to make sure each variable has appropriate value
        def errorChecking(protocolPhase, measurementType, numProbes, messageSize, serverDelay):
            if protocolPhase != 's':
                return False
            if measurementType != 'rtt' and measurementType != 'tput':
                return False
            if not numProbes.isdigit() or not messageSize.isdigit() or not serverDelay.isdigit():
                return False
            return True
        errors = errorChecking(protocolPhase, measurementType, numProbes, messageSize, serverDelay)
        
        # If errors, terminate, else send to Measurement Phase
        if (not errors):
            conn.sendall("404 ERROR: Invalid Connection Setup Message".encode('utf-8'))
            break
        else:
            conn.sendall("200 OK: Ready".encode('utf-8'))
            MP(conn, numProbes, serverDelay)

def MP(conn, numProbes, serverDelay):
    # Last package read, 
    last = 0
    
    # Listen for data until number of probes is matched
    while last < int(numProbes) - 1:
        data = conn.recv(1024)
        if len(data) > 0:
            time.sleep(int(serverDelay) / 1000)
            decodedData = data.decode('utf-8')
            parsedData = decodedData.split()
            seqNum = int(parsedData[1])
            print("Sequence Number: " + str(seqNum))
        
            if seqNum < last:
                conn.sendall("404 ERROR: Invalid Measurement Message".encode('utf-8'))
        
            last = seqNum
            conn.sendall(data)

CSP()