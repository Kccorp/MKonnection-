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
            "usage": "seach <filename>"
        }
    }

    print(f"{'Command':<15}{'Description and Usage':<50}")
    print("=" * 65)
    for command, info in commands.items():
        description = info["description"]
        usage = info["usage"]
        print(f"{command:<15}{description:<50}")
        print(f"{'':<15}{'Usage: ' + usage:<50}")
    print("\n")

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

