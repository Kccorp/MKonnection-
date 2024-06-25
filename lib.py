def print_help():
    commands = {
        "exit": {
            "description": "Close the server or disconnect from a session.",
            "usage": "exit"
        },
        "list": {
            "description": "List currently connected clients.",
            "usage": "list"
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
        }
    }

    print(f"{'Command':<15}{'Description and Usage':<50}")
    print("="*65)
    for command, info in commands.items():
        description = info["description"]
        usage = info["usage"]
        print(f"{command:<15}{description:<50}")
        print(f"{'':<15}{'Usage: ' + usage:<50}")

