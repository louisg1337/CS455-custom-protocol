import socket
import time

# HOST = input("IP Address: ")
# PORT = int(input("Host: "))
HOST = "csa3.bu.edu"
PORT = 58069  



def CSP():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    while True:
        protocolPhase = input("Protocol phase: ")
        measurementType = input("rtt or tput: ")
        numProbes = input("Number of probes: ")
        messageSize = input("Message size in B: ")
        serverDelay = input("Server delay (ms): ")

        message = protocolPhase + " " + measurementType + " " + numProbes + " " + messageSize + " " + serverDelay
        s.sendall(message.encode('utf-8'))

        response = s.recv(1024).decode('utf-8')
        print("\n" + response + "\n")
        
        if response == "200 OK: Ready":
            MP(s, measurementType, numProbes, messageSize, serverDelay)
        else:
            s.close()
            break
    
def MP(s, measurementType, numProbes, messageSize, serverDelay):
    print("Begin measuring period for... " + measurementType + "\n")
    numProbes = int(numProbes)
    messageSize = int(messageSize)
    serverDelay = int(serverDelay)
    payload = 'b' * messageSize
    responses = []
    for i in range(numProbes):
        timeStart = time.time()
        message = "m " + str(i) + " " + payload
        s.sendall(message.encode('utf-8'))
        
        while True:
            data = s.recv(1024).decode('utf-8')
            
            # Error handling
            if data == "404 ERROR: Invalid Measurement Message":
                print("404 ERROR: Invalid Measurement Message")
                s.close()
            
            
            if len(data) > 0: 
                timeEnd = time.time()
                timeDiff = (timeEnd - timeStart) * 1000
                print("Time (ms): " + str(timeDiff))
                print(data + "\n")
                responses.append(timeDiff)
                break
    
    avgRtt = (sum(responses) / numProbes) - serverDelay
    if measurementType == "rtt":
        print("Average RTT (ms): " + str(avgRtt) + "\n")
    else:
        throughput = (messageSize * 8) / (avgRtt / 1000)
        print("Average Throughput (bps): " + str(throughput) + "\n")
        
    print("///////////////////////\n")
    
CSP()