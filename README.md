# Chat

Program to create chats between clients. The server code can be deployed in a server (or in localhost) and
the clients can connect to it, create private rooms and chat with turns (one writes and the other has to wait until the other sends its response)

The server code could be deployed on an Amazon Web Server for example, and 2 friends could connect to talk.  , with AWS, the host_address in the server should be the private DNS address and the client ip to connect should be the public DNS address.

## Requirements
Python >= 3.7
Not external dependencies needed

## Installation
Easy localhost try
1. Move the server.py file to the server
2. Create .env.json (if not example will be copied into .env.json)

## Start server and clients
To start just run the corresponding file:

- To run the server -> 'python3 server.py' (replace python3 with py if you are in Windows)
- To run the client -> 'python3 client.py' (replace python3 with py if you are in Windows)

## Usage example



