import os

import pyfiglet


def print_help_client():
    commands = {
        "exit": {
            "description": "Close the client connection.",
            "usage": "exit"
        },
        "upload": {
            "description": "Upload a file from the server to the client.",
            "usage": "upload <file_path>"
        },
        "shell": {
            "description": "Open an interactive shell to execute commands on the client.",
            "usage": "shell"
        },
        "getuid": {
            "description": "Get the user identifier on the client.",
            "usage": "getuid"
        },
        "ipconfig": {
            "description": "Display the network configuration on the client.",
            "usage": "ipconfig"
        },
        "ls": {
            "description": "List files and directories in the client's current directory.",
            "usage": "ls"
        },
        "search": {
            "description": "Search any file in client file system",
            "usage": "seach <file path>"
        }
    }

    print_help(commands)


def print_help_manager():
    commands = {
        "exit": {
            "description": "Close the server or disconnect from a session.",
            "usage": "exit"
        },
        "list": {
            "description": "List currently connected clients.",
            "usage": "list"
        },
        "use": {
            "description": "Select a client to interact with.",
            "usage": "use <client_id>"
        }
    }
    print_help(commands)


def print_help(commands):
    print(f"{'Command':<15}{'Description and Usage':<50}")
    print("=" * 65)
    for command, info in commands.items():
        description = info["description"]
        usage = info["usage"]
        print(f"{command:<15}{description:<50}")
        print(f"{'':<15}{'Usage: ' + usage:<50}")


def print_mko_banner():
    # banner with pyfiglet
    print(pyfiglet.figlet_format("MKonnection-", font="slant"))


def print_mko_prefix():
    print("MKo > ", end="")


def print_mko_client(client_id):
    print(f"MKo (client {client_id}) > ", end="")


def use_manger(thread_id, thread_to_conn, client_queues):
    print(f"You are now using client {thread_id}")
    print_mko_client(thread_id)
    # Interact with the selected thread
    while True:
        sub_command = input()

        if sub_command.lower() == "exit":
            break

        if sub_command:
            conn = thread_to_conn[thread_id]
            client_queues[conn].put(sub_command)

        if sub_command == "close":
            return "close"
        elif sub_command == "shell":
            return "shell"


def upload_file(file_path, conn):
    file_size = os.path.getsize(file_path)
    conn.send(file_size.to_bytes(8, 'big'))

    nbr_of_dot = 1
    with open(file_path, "rb") as file:
        while chunk := file.read(1024):
            conn.send(chunk)
            percent = conn.recv(1024).decode('utf-8')
            nbr_of_dot = print_progress(percent, nbr_of_dot)


def print_progress(progress, nbr_of_dot):
    print("\rReceiving (" + progress + "%)" + "." * nbr_of_dot, end="", flush=True)
    if nbr_of_dot == 3:
        return 1
    else:
        return nbr_of_dot + 1


def download_file(file_path, conn):
    if '/' in file_path:
        filename = file_path.split("/")[-1]
    elif '\\' in file_path:
        filename = file_path.split("\\")[-1]
    else:
        filename = file_path

    # receive the file size
    file_size = int.from_bytes(conn.recv(8), 'big')
    print(f"Expected file size: {file_size} bytes")

    # receive the file
    nbr_of_dot = 1
    with open(filename, "wb") as file:
        received = 0
        while received < file_size:
            chunk = conn.recv(min(1024, file_size - received))
            if not chunk:
                raise EOFError('Connection closed before receiving all the data')
            file.write(chunk)
            received += len(chunk)
            # calculate progress
            progress = str(round(((received / file_size) * 100)))
            nbr_of_dot = print_progress(progress, nbr_of_dot)


def interact_shell(conn, client_id):
    print(f"MKo Shell (client {client_id}) > ", end="")
    conn.send("shell".encode('utf-8'))

    while True:
        command = input()

        if command.lower() == "exit":
            conn.send(command.encode('utf-8'))
            print(conn.recv(1024).decode('utf-8'))
            break

        if command.lower() == "":
            continue

        conn.send(command.encode('utf-8'))
        output = conn.recv(1024).decode('utf-8')
        print(output)

        print(f"MKo Shell (client {client_id}) > ", end="")
