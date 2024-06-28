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
        else:
            print("Unknown command. Try 'help' or '?' to display help", end="\n\n")
            return "unknown"

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
            print(f"Le fichier {file_path} n'existe pas.")
            return "error"

        return command

        # print(f"Uploading {file_path}...")
        # conn.send(command.encode('utf-8'))
        #
        # file_size = os.path.getsize(file_path)
        # conn.send(file_size.to_bytes(8, 'big'))
        # print(f"Sent file size: {file_size} bytes")
        #
        # with open(file_path, "rb") as file:
        #     while (chunk := file.read(1024)):
        #         conn.send(chunk)
        #
        # print("File uploaded successfully")

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

    # def upload(self, file_path):
    #     if not os.path.isfile(file_path):
    #         print(f"Le fichier {file_path} n'existe pas.")
    #         return
    #     print(f"Uploading {file_path}...")
    #     conn.send(command.encode('utf-8'))
    #     file_size = os.path.getsize(file_path)
    #     conn.send(file_size.to_bytes(8, 'big'))
    #     print(f"Sent file size: {file_size} bytes")
    #     with open(file_path, "rb") as file:
    #         while chunk := file.read(1024):
    #             conn.send(chunk)
    #     print("File uploaded successfully")
