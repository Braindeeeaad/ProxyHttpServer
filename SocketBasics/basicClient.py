import socket
import pickle #you can Pickle your own personal object and send that through socket connections 

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.86.37"
ADDR = (SERVER,PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length)) # adds padding to the string based off how many blank spaces are neeeded to fill header
    client.send(send_length)
    client.send(message)
    print(client.recv(2048).decode(FORMAT))

send("Hello WOrld")
input()#forces you to press space before continuing code(blocking line i think?)
send("Hello BBG")
input()
send(DISCONNECT_MESSAGE)