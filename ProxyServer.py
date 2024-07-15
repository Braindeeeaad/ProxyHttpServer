import socket
import threading
import signal
import ssl

HEADER = 800 # The first message from the client to the server is going to be a header of 64 byes
            # the first recieved message will specify the number of bytes the next recieved message is going to contain
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
#print(socket.gethostname())# gets device name
SERVER = socket.gethostbyname(socket.gethostname()) #Get's the current devices name and returns it's ip-address via its name
ADDR = (SERVER, PORT)
serverInfo = {'BLACKLISTDOMAINS':["tiktok.com"]}


class proxyServer:
    def __init__(self):
        # shutdown on Ctrl+c
        signal.signal(signal.SIGINT, self.exit_gracefully)
        #create a TCP socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Re-use the socket
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        #bind the socket to a public host, and a port
        self.server.bind(ADDR)

        self.server.listen(10)
        print(f"[LISTENING] Server is listening on {SERVER}")
        self.__clients = {}


    def exit_gracefully(self,signum,frame):
        """
                Handle the signal for a graceful shutdown.

                Parameters:
                signum (int): The signal number.
                frame (frame object): The current stack frame.
                """
        print("Shutdown signal received")

        self.server.close()

        #shutting down other threads

        for t in threading.enumerate():
            if t is threading.main_thread():
                continue
            t.join()

        exit(0)

    def handle_http(self, address, conn, request):
        webserver,port = address
        print(f'Webserver:{webserver}, Port:{port}')


        remote_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_server.settimeout(10.0)
        remote_server.connect((webserver, port))  # connects the tcp socket to the remote server
        remote_server.sendall(request.encode(FORMAT))

        # Blocked portion of code, waits for the server to send back the info and sends it to client
        self.forward(remote_server, conn)
        conn.close()
        remote_server.close()

    def handle_https(self, address, conn, request):
        webserver,port = address
        if port == 80:
            port = 443

        # wraps in ssl required for https
        context = ssl.create_default_context()
        remote_server = socket.create_connection((webserver,port))
        remote_server = context.wrap_socket(remote_server,server_hostname=webserver)
        remote_server.sendall(request.encode(FORMAT))


        # Blocked portion of code, waits for the server to send back the info and sends it to client-> thats why there is another thread
        # We don't restrict the flow of data for one lane, rather have bidirectional transfer of data

        #threading.Thread(target=self.forward, args =(conn,remote_server)).start()

        # Blocked portion of code, waits for the server to send back the info and sends it to client
        self.forward(remote_server,conn)
        conn.close()
        remote_server.close()

    def forward(self,source,destination):
        data = source.recv(4096)
        destination.sendall(data)
        '''
        while True:
            try:
                if len(data) == 0:
                    break
                destination.sendall(data)
            except Exception as e:
                print(f"Data transfer from source to destination failed :{e}")
                break 
        '''



    def extractADDR(self,url):
        # Finding Destination address tuple -> (addr,port) from url
        http_pos = url.find("://")

        if http_pos == -1:
            temp = url
        else:
            temp = url[(http_pos + 3):]

        port_pos = temp.find(":")

        webserver_pos = temp.find("/")

        if webserver_pos == -1:
            webserver_pos = len(temp)

        webserver = ""
        port = -1
        if port_pos == -1 or webserver_pos < port_pos:
            # No specific port, default to port 80
            port = 80 #80
            webserver = temp[:webserver_pos]
        else:
            port = int(temp[(port_pos + 1):webserver_pos])
            webserver = temp[:port_pos]
        return (webserver, port)


    def handle_client(self,conn, addr):
        print(f"[NEW CONNECTION] {addr} connected.")

        try:
            request = conn.recv(HEADER).decode(FORMAT)
            if not request:
                return
            first_line = request.split('\n')[0]
            method = first_line.split(' ')[0]
            url = first_line.split(' ')[1]

            remote_server_info = self.extractADDR(url)

            if self._checkDomainInBlackList(url):
                conn.close()
                return
            if method == 'CONNECT':
                self.handle_https(remote_server_info, conn, request)
            else:
                self.handle_http(remote_server_info, conn, request)

        except Exception as e:
            print(f'Error handling client {addr}: {e}')
        finally:
            conn.close()










    def _getClientName(self,client_address):
        return f"Client-{client_address}"

    def _checkDomainInBlackList(self,url):
        for blackListedDomain in serverInfo["BLACKLISTDOMAINS"]:
            if blackListedDomain in url:
                return True
        return False
    def start(self):
        while True:
            conn, addr = self.server.accept()  # server.accept()-> we wait for a new connection, when it occurs we save that connection
            # through its address and conn, an object which we can send data back to the connection
            thread = threading.Thread(name = self._getClientName(addr) ,target=self.handle_client, args=(conn,addr))  # makes a thread for each connection so we can process each client conncurently, b/c we utilize blocking lines of code
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")  # we do -1, because our main server thread is counted threading.active_count()


if __name__ == '__main__':
    pserver = proxyServer()
    pserver.start()
    print("[STARTING]")
