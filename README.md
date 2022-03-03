# RoomChat

Program to create secure chats between clients. The server code can be deployed in a server (or in your computers localhost) and the clients can connect to it, create private rooms and chat with turns (one writes and the other has to wait until the other sends its response). It's just a project that implements threads to handle multiple socket connections with RSA msg encryption, and may serve as a base for other similar projects. The server code also provides some basic features of logging and statistical analysis of your server state, active connections and ips info in real time and provides a blocking ip function to block connections from ips which tried to connect 3 times with incorrect credentials.

The server code could be deployed for example on an Amazon Web Server, and X people could connect to talk online simultaneously in different private rooms of 2 people size. In concrete, with AWS the host_address in the server should be the private DNS address and the client ip to connect should be the public DNS address.

I have prepared other 2 branches 'server' and 'client' with the necessary code and a short README of how to run each one. The idea is to download the code with:
```
git clone --branch server https://github.com/pgmesa/chat-rooms/
```
or 
```
git clone --branch client https://github.com/pgmesa/chat-rooms/
```
and then create your '.env.json' file following the '.env_example.json'. When done, you could send your friends the client configured (e.g. in a .zip file) with the server password and where to connect to establish connection with them. 

## Requirements
- Python >= 3.7
- (Only for the client) Intstall my cryptographic PyPI package for RSA encryption (requirements.txt)
```
pip install -r requirements.txt
```
I have another branch in this git called 'no-rsa' that doesn't implement RSA encryption and that also doesn't need you to install any external dependencies (just move the server.py and client.py file to where you want to use it)
```
git clone --branch no-rsa https://github.com/pgmesa/chat-rooms/
```

## Installation
To make an easy test:
1. Create a '.env.json' file with the variables specified in the '.env_example.json' (copy and paste), change them if you want.
```
{
    "HOST_ADDRESS": "localhost",
    "HOST_PORT": 8888,
    "SERVER_PASSWORD": "test12345",
    "SERVER_NAME": "PyChat",
    "USER_NAME": "Unknown" 
}
```
2. Open 3 terminals in the projects directory. Run the server.py in one of them, and the 'client.py' in the other
3. Create a room with one client and connect with that room_id with the other client
4. Send msgs and enjoy 

To deploy the code in a server with the intention to talk to someone over the internet:
1. Move the 'server.py' file to your online server (AWS, Azure, Google Cloud...)
2. Create the '.env.json' file in the same directory as the file and change the variables to fit your server (remember to open the server port you specify in the '.env.json' file before you run the program)
3. Run the 'server.py' file
4. Create the '.env.json' file for the 'client.py' (the password must be the same as the one in the server '.env.json' file)
5. Tell your friend to do the same as you
5. Both run the 'client.py' file. One should create a room and the other must connect to that room.
6. Send msgs and enjoy (All msgs will be encrypted only you and the person on the other side can see it)

## Start server and Clients
To start just run the corresponding file:
- To run the server -> 'python3 server.py' (replace 'python3' with 'py' or 'python' if you are in Windows)
- To run the client -> 'python3 client.py' (replace 'python3' with 'py' or 'python' if you are in Windows)

## Statistics of the program
IPs Info
```
{
    "127.0.0.1": {
        "Pablo": {
            "num-connections": 5,
            "num-wrong-credentials": 0,
            "blocked-times": 0
        }
    }
}
```
Server State
```
{
    "visits": 1,
    "active-threads": 1,
    "rooms": {
        "num": 1,
        "ids": [
            "1KYAUPMB9KRT"
        ]
    },
    "active-chats": {
        "num": 0,
        "ids": []
    }
}
```

