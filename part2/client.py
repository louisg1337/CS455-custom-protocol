import socket
import time

# HOST = input("IP Address: ")
# PORT = int(input("Host: "))
HOST = "csa3.bu.edu"
PORT = 58069  

# Connection set up phase function that handles 
# getting the connection established and error checking
def CSP():
    # Initialization code to set up socket connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    while True:
        # Ask user for initial connection phase protocol info
        protocolPhase = input("Protocol phase: ")
        measurementType = input("rtt or tput: ")
        numProbes = input("Number of probes: ")
        messageSize = input("Message size in B: ")
        serverDelay = input("Server delay (ms): ")  

        # Combine all user info and send over to the server
        message = protocolPhase + " " + measurementType + " " + numProbes + " " + messageSize + " " + serverDelay
        s.sendall(message.encode('utf-8'))

        # Attempt to get response from server
        response = None
        timeout = time.time() + 2.0
        while (time.time() < timeout):        
            response = s.recv(1024).decode('utf-8')
            if (response != None):
                print("\n" + response + "\n")
                break
        
        # If good repsonse, send to measurement phase, if not, terminate
        if response == "200 OK: Ready":
            MP(s, measurementType, numProbes, messageSize, serverDelay)
        else:
            s.close()
            break
    
# This is the mesaurement phase function for our TCP experiment. Client
# gets sent into here if the server verified their request to begin. 
def MP(s, measurementType, numProbes, messageSize, serverDelay):
    # Variable initializations to get all data needed to send to server
    print("Begin measuring period for... " + measurementType + "\n")
    numProbes = int(numProbes)
    messageSize = int(messageSize)
    serverDelay = int(serverDelay)
    payload = 'b' * messageSize
    responses = []
    
    # Set a flag incase need to abort experiment b/c of packet loss
    abort = False
    
    # Send numProbes amount of messages to the server
    for i in range(numProbes):
        # Start the timer and send message 
        timeStart = time.time()
        message = "m " + str(i) + " " + payload
        s.sendall(message.encode('utf-8'))
        
        # Keep track of what bytes have been sent so far
        currentDataSize = 0
        allData = b""
        
        # Continue listening to server to get entire message back
        while currentDataSize < messageSize:
            data = s.recv(messageSize + 4)
            decodedData = data.decode('utf-8')
            
            # Error handling
            if decodedData == "404 ERROR: Invalid Measurement Message":
                print("404 ERROR: Invalid Measurement Message")
                s.close()
                abort = True
                break
            if decodedData == "404 ERROR: Packet lossed, redo experiment":
                print("Packet was lost during experiment, redo it!")
                abort = True
                break
            
            # Keep track of how much data was sent, and what data
            currentDataSize += len(data)
            allData += data
            
            
        # If packet loss, break out of for loop   
        if (abort): 
            break
        
        # Echo message back to user with timer
        timeEnd = time.time()
        timeDiff = (timeEnd - timeStart) * 1000
        print("Time (ms): " + str(timeDiff))
        print(allData.decode('utf-8') + "\n")
        responses.append(timeDiff)
        
            
    # If packet loss, don't display any results from below
    if (abort):
        return
    
    # Calculate and display Avg RTT or Avg TPUT
    avgRtt = (sum(responses) / numProbes) - serverDelay
    if measurementType == "rtt":
        print("Average RTT (ms): " + str(avgRtt) + "\n")
    else:
        throughput = (messageSize * 8) / (avgRtt / 1000)
        print("Average Throughput (bps): " + str(throughput) + "\n")
        
    print("///////////////////////\n")

# Call connection startup phase to begin the client's search 
CSP()