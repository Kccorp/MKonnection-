# MKonnection

MKonnection is a simple client-server application written in Python. It allows for basic command execution and file transfer between the client and the server.

## Features

- Command execution
- File transfer
- Multi-threaded server
- Encrypted communication

## Usage

### Server

To start the RAT server, run the following command:

```bash
pip install -r requirements.txt
python main.py
```

### Client

To start the RAT client, run the following command:

```bash
python client.py
```

## Commands

The following commands are available:

- `help` - Display help message
- `exit | close` - Exit connections
- `shell` - Start an interactive shell
- `download <file>` - Download a file from the server
- `upload <file>` - Upload a file to the server
- `screenshot` - Take a screenshot of the client's screen [!! not working on wayland !!]
- `hashdump` - Dump password hashes from the client


Usual commands:
- `sysinfo` - Get system information of the client
- `ipconfig` - Get the IP configuration of the client 
- `search` - Search for files on the client
- `cd` - Change directory on the client
- `pwd` - Get the current directory of the client