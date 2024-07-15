import socket
import threading

HEADER = 64 # The first message from the client to the server is going to be a header of 64 byes
            # the first recieved message will specify the number of bytes the next recieved message is going to contain
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
#print(socket.gethostname())# gets device name
SERVER = socket.gethostbyname(socket.gethostname()) #Get's the current devices name and returns it's ip-address via its name
ADDR = (SERVER, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #makes a socket object that utilizes ipv4 IP address for connections and streams data to and fro
server.bind(ADDR) #Binding socket to a specific address, so anything that connects to that address hits the server socket

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    while True:
        msg_length = conn.recv(HEADER).decode(FORMAT)#decode the message from utf-8 bytes format to string #"blocking" line of code which waits for connection to send a mssg
                         # The argument to the recv() method is the number of bytes to recieve
        if msg_length: #Initally when connection is established a "blank" mssg is sent so it will screw up our string-> int conversion, so we check if the mssg is not null
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                break
            print(f"[{addr}] {msg}")
            conn.send("Msg recieved".encode(FORMAT))


    conn.close()

def start():
    server.listen()#listening for new connections
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept() #server.accept()-> we wait for a new connection, when it occurs we save that connection
                                     #through its address and conn, an object which we can send data back to the connection
        thread = threading.Thread(target=handle_client, args =(conn,addr)) #makes a thread for each connection so we can process each client conncurently, b/c we utilize blocking lines of code
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}") # we do -1, because our main server thread is counted threading.active_count()

if __name__ == '__main__':
    print("[STARTING]")
    start()