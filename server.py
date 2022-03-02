
# Built-in
import os
import copy
import time
import json
import sys
import shutil
import socket
import random, string
from pathlib import Path
from threading import Thread, Lock, Event

dir_ = Path(os.getcwd()).resolve()
env_path = dir_/'.env.json'

def config(key) -> any:
    if not os.path.exists(env_path):
        shutil.copy(dir_/'.env_example.json', env_path)
    with open(env_path, 'r') as file:
        env_dict = json.load(file)
    return env_dict[key]

# Environment variables
try:
    HOST_ADDRESS = config('HOST_ADDRESS')
    HOST_PORT = config('HOST_PORT')
    SERVER_PASSWORD = config('SERVER_PASSWORD')
except Exception as err:
    print(err)
    exit(1)

stats_fname = './stats.json'
stats_path = dir_/stats_fname
log_dir = 'logs'
log_dir_path = dir_/log_dir

block_ip_time = 300 # Seconds
stats_squema = {
    "visits": 0,
    "active-threads": 0,
    "rooms": {"num": 0, "ids":[]},
    "active-chats": {"num": 0, "ids":[]}
}

exit_event = Event()

# Communication agreements
SUCCESS = "0"; FAIL = "1"
 
class SocketListener(Thread):
    def run(self):
        self.num_connections = 0; self.threads = []
        self.rooms = {}; self.active_rooms = []
        self.lock = Lock(); self.blocked_ips = {}; self.ips_that_fail = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_socket.bind((HOST_ADDRESS, HOST_PORT)) 
        except socket.error as err:
            print("[!]", str(err))
        else:
            print("[%] Waiting for conexions...")
            self.server_socket.listen(1)
            while True:
                client, address = self.server_socket.accept()
                ip = address[0]
                # Comprobamos si es una ip bloqueada
                if ip in self.blocked_ips:
                    t0 = self.blocked_ips[ip]
                    tf = time.time()
                    remaining_t = block_ip_time - (tf - t0)
                    if remaining_t < block_ip_time:
                        print(f"Connection Refused '{ip}' is in blocked ips -> '{round(remaining_t, 2)}'s remaining")
                        client.close()
                        continue
                    else:
                        self.blocked_ips.pop(ip)
                # Esperamos la contraseña
                password = client.recv(2048).decode('utf-8')
                if password != SERVER_PASSWORD:
                    print(f"Connection Refused -> '{ip}', wrong password '{password}'")
                    if ip not in self.ips_that_fail:
                        self.ips_that_fail[ip] = 0
                    self.ips_that_fail[ip] += 1
                    if self.ips_that_fail[ip] >= 3:
                        print("Blocking IP due to 3 failed attempts")
                        self.blocked_ips[ip] = time.time()
                        self.ips_that_fail.pop(ip)
                    client.send(FAIL.encode())
                    client.close()
                    continue
                client.send(SUCCESS.encode())
                print("[%] Connection stablished with ->", ip + ':' + str(address[1]))
                thread = Thread(target=self.threaded_client, args=(client,))
                self.threads.append(thread)
                self.num_connections += 1
                thread.start()
                self.update_stats()
                
    def update_stats(self, reset:bool=False, _shutting_thread=False):
        stats = self.load_stats()
        active_threads = self.check_threads(kill_all=reset)
        if _shutting_thread: active_threads -= 1
        if reset:
            visits = stats['visits']
            stats = copy.copy(stats_squema)
            stats['visits'] = visits
        else:
            stats['visits'] = self.num_connections
            stats['active-threads'] = active_threads
            stats['rooms'] = {"num": len(self.rooms), "ids": list(self.rooms.keys())}
            stats['active-chats'] = {"num": len(self.active_rooms), "ids": self.active_rooms}
        self.lock.acquire()
        try:
            with open(stats_path, 'w') as file:
                json.dump(stats, file, indent=4)
        finally:
            self.lock.release()
    
    def load_stats(self) -> dict:
        if not os.path.exists(stats_path):
            stats = copy.copy(stats_squema)
        else:
            self.lock.acquire()
            try:
                with open(stats_path, 'r') as file:
                    stats = json.load(file)
            finally:
                self.lock.release()
        return stats
        
    def check_threads(self, kill_all:bool=False) -> int:
        active_threads = 0
        delete_buffer = []
        if kill_all:
            for sock in self.rooms.values():
                try: sock.close()
                except: pass
        time.sleep(0.5)
        for t in self.threads:
            if t.is_alive():
                active_threads += 1
            else:
                delete_buffer.append(t)
        for t in delete_buffer:
            self.threads.remove(t)
        return active_threads
    
    def threaded_client(self, socket_connection):        
        socket_connection.send(str.encode('Welcome to the Server'))
        data = socket_connection.recv(2048)
        if not data:
            print("Wrong client response, finishing conexion")
            socket_connection.close()
        else:
            data = data.decode('utf-8')
            if data == "0":
                room_id = self._generate_id()
                print(f"Creating room with id '{room_id}'")
                self.create_chat(room_id, socket_connection)
            else:
                room_id = data
                print(f"Joining room '{room_id}'")
                self.establish_clients_connection(room_id, socket_connection)
        self.update_stats(_shutting_thread=True)
        sys.exit()
    
    def _generate_id(self, size:int=12) -> str:
        # Size: number of characters in the string.  
        # call random.choices() string module to find the string in Uppercase + numeric data.  
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = size))    
        return str(ran)  
    
    def create_chat(self, room_id:str, socket_connection):
        self.lock.acquire()
        try:
            self.rooms[room_id] = socket_connection
            socket_connection.sendall(room_id.encode())
        finally:
            self.lock.release() 
        self.update_stats()
        try:
            flag = socket_connection.recv(1024).decode()
            if flag == FAIL or flag == "":
                raise socket.error()
        except socket.error:
            self.rooms.pop(room_id)
            print(f"Room '{room_id}' canceled")
    
    def establish_clients_connection(self, room_id, second_connection):
        first_connection = None; reply = FAIL
        try:
            self.lock.acquire()
            if room_id in self.rooms:
                first_connection = self.rooms[room_id]
                reply = SUCCESS
        except Exception as err:
            print(err)
        finally:
            self.lock.release()
        second_connection.sendall(reply.encode('utf-8'))
        if first_connection is not None:
            first_connection.sendall(reply.encode('utf-8'))
            self.start_chat(room_id, first_connection, second_connection)
           
    def start_chat(self, room_id, socket1, socket2):
        self.lock.acquire()
        self.rooms.pop(room_id)
        self.lock.release()
        self.active_rooms.append(room_id)
        self.update_stats()
        try:
            # Primero habla el que se une a la sala
            while True:
                # set to True event
                if exit_event.is_set():
                    break
                recv_msg_from2 = socket2.recv(2048)
                if not recv_msg_from2: break
                socket1.sendall(recv_msg_from2)
                recv_msg_from1 = socket1.recv(2048)
                if not recv_msg_from1: break
                socket2.sendall(recv_msg_from1)
        except socket.error: pass
        finally:
            print(f"[!] Closing connection in room '{room_id}'")
            self.active_rooms.remove(room_id)
            print("Active Chat Rooms:", len(self.active_rooms))
            socket1.close(); socket2.close()
    
    def close(self):
        print("[%] Closing connection...")
        # Reseteamos las estadisticas tambien (menos numero de visitas)
        exit_event.set()
        self.update_stats(reset=True)
        self.server_socket.close()

def signal_handler(signum, frame):
    exit_event.set()

try:
    sl = SocketListener()
    sl.start()
    print('-> Socket is listening, press any ctrl-c to abort...')
    while sl.is_alive(): pass
except Exception as err:
    print(f"[!] {err}")
except KeyboardInterrupt: pass
finally:
    print("[%] Closing Server")
    sl.close()
    pid = os.getpid()
    os.kill(pid,9)