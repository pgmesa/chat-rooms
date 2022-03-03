# Chat Client

Program to create secure chats between clients. The server code can be deployed in a server (or in your computers localhost) and the clients can connect to it, create private rooms and chat with turns (one writes and the other has to wait until the other sends its response).

Link to complete github project -> https://github.com/pgmesa/chat-rooms

## Installation
1. Install the cryptographic dependencies (my own PyPI package) that the client needs to encrypt msgs with RSA (public-private key pair) 
```
pip install -r requirements.txt
```
2. Change the USER_NAME variable of the '.env.json' file with yours

## Run the client
- Windows
```
python client.py
```
or 
```
py client.py
```
- Linux and MAC
```
python3 client.py
```