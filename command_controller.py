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

    def getuid(self):
        if self.os_client == "Linux":
            return "id"
        elif self.os_client == "Windows":
            return "whoami"

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

