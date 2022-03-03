# Server Chat

Program to create secure chats between clients. The server code can be deployed in a server (or in your computers localhost) and the clients can connect to it, create private rooms and chat with turns (one writes and the other has to wait until the other sends its response). It's just a project that implements threads to handle multiple socket connections with RSA msg encryption, and may serve as a base for other similar projects. The server code also provides some basic features of logging and statistical analysis of your server state, active connections and ips info in real time and provides a blocking ip function to block connections from ips which tried to connect 3 times with incorrect credentials.

The server code could be deployed for example on an Amazon Web Server, and X people could connect to talk online simultaneously in different private rooms of 2 people size. In concrete, with AWS the host_address in the server should be the private DNS address and the client ip to connect should be the public DNS address.

Link to complete github project -> https://github.com/pgmesa/chat-rooms

## Run the server
- Windows
```
python server.py
```
or 
```
py server.py
```
- Linux and MAC
```
python3 server.py
```

## Reset server files
Deletes './ips.json', './stats.json' and all the logs in './log'
```
python3 server.py reset
```

