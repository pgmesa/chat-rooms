
import os
import json
import sys
import socket
from threading import Thread
from pathlib import Path

dir_ = Path(os.getcwd()).resolve()
env_path = dir_/'.env.json'

def config(key) -> any:
    if not os.path.exists(env_path):
        raise Exception(f"Not '.env.json' file in '{dir_}'")
    with open(env_path, 'r') as file:
        env_dict = json.load(file)
    return env_dict[key]

# Environment variables
try:
    HOST_ADDRESS = config('HOST_ADDRESS')
    HOST_PORT = config('HOST_PORT')
    SERVER_PASSWORD = config('SERVER_PASSWORD')
    NAME = config('USER_NAME')
except Exception as err:
    print(err)
    exit(1)

# Communication agreements
SUCCESS = "0"; FAIL = "1"

class ChatClient(Thread):
    
    def run(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print(f"Connecting to {HOST_ADDRESS}:{HOST_PORT}")
            self.client_socket.connect((HOST_ADDRESS, HOST_PORT))
            # Send User name
            self.client_socket.send(NAME.encode('utf-8'))
        except socket.error as err:
            print("[!]", str(err))
            return
        else:
            print("Connection established")
            
        # Send password
        try:
            self.client_socket.send(SERVER_PASSWORD.encode('utf-8'))
            login_outcome = self.client_socket.recv(1024).decode()
            if login_outcome == FAIL:
                print("[!] Seems that the password is incorrect, conexion refused")
                return
            elif login_outcome == SUCCESS:
                # Welcome Msg
                print("Credentials are correct")
                response = self.client_socket.recv(1024)
                print(response.decode('utf-8'))
        except socket.error:
            print("[!] Seems the server blocked this ip due to more than 3 failed attemps to connect with incorrect password")
            return
        try:
            print("+ 0 for creating a chat room")
            print("+ 1 for entering an existing chat room")
            while True:
                answer = str(input('-> Introduce your choice: '))
                if answer != "0" and answer != "1":
                    print(f"[!] Wrong Answer (must be 0 or 1 not '{answer}')")
                else:
                    break
            if answer == "0":
                self.client_socket.send(str.encode(answer))
                room_id = self.client_socket.recv(1024).decode('utf-8')
                print(f"Your room-id is: '{room_id}'")
                print("Waiting for player conexion...")
                connection_outcome = self.client_socket.recv(1024).decode('utf-8') 
                self.client_socket.send(SUCCESS.encode())
            if answer == "1":
                while True:
                    room_id = str(input("Introduce your room id: "))
                    if answer == "":
                        print(f"[!] Wrong Answer (can't be void)")
                    else:
                        break
                self.client_socket.send(str.encode(room_id))
                connection_outcome = self.client_socket.recv(1024).decode('utf-8') 
            
            def valid_msg(msg:str) -> bool:
                if msg != "": return True
                return False
            
            if connection_outcome == SUCCESS:
                # Send the user name
                self.client_socket.sendall(NAME.encode())
                # Recieve other client name
                other_client = self.client_socket.recv(1024).decode('utf-8')
                print(f"[%] Connection Succeed, connected with '{other_client}'")
                if answer == "1":
                    while True:
                        msg = str(input(f"=> Write your first msg here to '{other_client}': "))
                        if valid_msg(msg): break
                        print("[!] Can't send void msg")
                    self.client_socket.send(str.encode(msg))   
                while True:
                    print(f"Waiting for '{other_client}' to respond...")
                    recv_msg = self.client_socket.recv(1024)
                    if not recv_msg: break
                    print(f"+ '{other_client}' says:", recv_msg.decode('utf-8'))
                    while True:
                        msg = str(input(f"=> Write your msg here to '{other_client}': "))
                        if valid_msg(msg): break
                        print("[!] Can't send void msg")
                    self.client_socket.send(str.encode(msg))
            elif connection_outcome == FAIL:
                print("[!] Connection Failed")
        except socket.error as err:
            print("[!]", str(err))

    def close(self):
        print("[%] Closing connection...")
        self.client_socket.close()
       
client = ChatClient()
client.start()
try:
    while client.is_alive(): pass
except KeyboardInterrupt: pass
finally:
    print("[%] Closing client...")
    client.close()
    #sys.stdout = open(os.devnull, 'w')
    pid = os.getpid()
    os.kill(pid,9)