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

        # Response received from server
        response = s.recv(35000).decode('utf-8')
        print("\n" + response + "\n")
        
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
    
    # Send numProbes amount of messages to the server
    for i in range(numProbes):
        # Start the timer and send message 
        timeStart = time.time()
        message = "m " + str(i) + " " + payload
        s.sendall(message.encode('utf-8'))
        
        # Wait and listen for the echo response back from the server
        while True:
            data = s.recv(35000).decode('utf-8')
            
            # Error handling
            if data == "404 ERROR: Invalid Measurement Message":
                print("404 ERROR: Invalid Measurement Message")
                s.close()
            
            # If we get back valid data, echo the message to the client
            # and display the time it took to get to back to them
            if len(data) > 0: 
                timeEnd = time.time()
                timeDiff = (timeEnd - timeStart) * 1000
                print("Time (ms): " + str(timeDiff))
                print(data + "\n")
                responses.append(timeDiff)
                break
    
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