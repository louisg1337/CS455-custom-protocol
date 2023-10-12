import socket
import time

HOST = input("IP Address: ")
PORT = int(input("Port: "))

# Connection set up phase function that handles 
# getting the connection established and error checking
def CSP():
    # Boilerplate code to set up the socket and start
    # listening for potential user to connect
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    print(f"Connected by {addr}")
    
    # If someone is connected, constantly listen for any
    # data that might be sent.
    while True:
        # Receive data and parse it to be used below
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
            
        # Put parsed data to variable name
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
            MP(conn, numProbes, serverDelay, messageSize)

# This is the mesaurement phase function for our TCP experiment. User gets sent
# into here if and only if they passed pre requisite checks for their setup connection.
def MP(conn, numProbes, serverDelay, messageSize):
    # Last package read, use this to make sure packages sent in right order
    last = 0
    messageSize = int(messageSize)
    
    # Listen for data until number of probes is matched
    while last < int(numProbes) - 1:
        print("-----------------------")
        currentDataSize = 0
        sendBack = b""
        
        # Set a timeout in case packet gets lost
        timeout = time.time() + 2.0
        
        # Keep on listening for data until the entire message is received
        while currentDataSize < messageSize:
            # Receive data
            data = conn.recv(messageSize)
            parsedData = data.decode('utf-8').split()
            print(len(data))
            
            # Packet potentially lost, return error to redo experiment
            if (time.time() >= timeout):
                # Send error and break out of loops
                conn.sendall("404 ERROR: Packet lossed, redo experiment".encode('utf-8'))
                last = int(numProbes)
                break
            
            # If we get valid data then
            if (len(data) > 0):
                # If received packet with header info
                if len(parsedData) > 1:         
                    # Parse data to extract the sequence number
                    seqNum = int(parsedData[1])
                    print("Sequence Number: " + str(seqNum))
                
                    # Handle if packets are out of order
                    if seqNum < last:
                        # Send error and break out of loop
                        conn.sendall("404 ERROR: Invalid Measurement Message".encode('utf-8'))
                        last = int(numProbes)
                        break
                    last = seqNum
                    
                    # Add only payload to currentBitSize
                    currentDataSize = len(parsedData[2])
                else:
                    # Only payload, so just add len(data)
                    currentDataSize += len(data)
                    
                # Combine all data
                sendBack += data
        
        # Server delay if needed
        time.sleep(int(serverDelay) / 1000)        
        
        # Echo message back to client
        conn.sendall(sendBack)    
        
        

# Calls connection phase to start up server
CSP()